import hashlib
from pathlib import Path
from unittest.mock import MagicMock
import json

import pandas as pd

from src.calendar_adapter import load_and_verify_calendar, compute_canonical_hash, CalendarMetadata
from historical_acquisition.yfinance_adapter import YFinanceDataSource
from src.dataset_preparation import prepare_dataset
from src.dataset_store import DatasetStore


def test_provider_to_staging_and_qualification_integration(tmp_path):
    # 1. Build a complete valid calendar dict in-memory to ensure all required fields are present.
    cal_data = {
        "calendar_id": "NYSE_DEFAULT",
        "calendar_version": "1.0.0",
        "exchange": "NYSE",
        "market": "US_EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [
            {
                "date": "2026-01-02",
                "open": "09:30:00",
                "close": "16:00:00",
                "is_trading_day": True
            },
            {
                "date": "2026-01-05",
                "open": "09:30:00",
                "close": "16:00:00",
                "is_trading_day": True
            }
        ]
    }
    cal_data["sha256"] = compute_canonical_hash(cal_data)

    dynamic_cal_path = tmp_path / "valid_calendar.json"
    dynamic_cal_path.write_text(json.dumps(cal_data), encoding="utf-8")

    calendar_meta = load_and_verify_calendar(dynamic_cal_path)
    assert calendar_meta.calendar_id == "NYSE_DEFAULT"

    # 2. Mock the external downloader callable behind the real provider adapter.
    mock_downloader = MagicMock()

    mock_df = pd.DataFrame(
        {
            "Open": [100.0, 102.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 101.0],
            "Close": [104.0, 105.5],
            "Volume": [1000000, 1200000],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-05"]),
    )

    mock_downloader.return_value = mock_df

    adapter = YFinanceDataSource(downloader=mock_downloader)

    # 3. Acquire through the real provider adapter.
    bars = adapter.fetch_daily(
        "AAPL",
        "2026-01-02",
        "2026-01-05",
    )

    # Verify boundary call contract
    mock_downloader.assert_called_once_with(
        "AAPL",
        start="2026-01-02",
        end="2026-01-05",
        interval="1d",
        progress=False,
        auto_adjust=False,
    )

    raw_bytes = bars.raw_csv_bytes
    assert isinstance(raw_bytes, bytes)
    raw_acquisition_sha = hashlib.sha256(raw_bytes).hexdigest()

    # 4. Byte-exact staging: no parsing or re-serialization.
    staged_csv_path = tmp_path / "staged_aapl.csv"
    staged_csv_path.write_bytes(raw_bytes)

    assert staged_csv_path.read_bytes() == raw_bytes

    # 5. Qualify and store using the real P4.3 path.
    store = DatasetStore(root_dir=tmp_path / "store")

    result = prepare_dataset(
        csv_path=staged_csv_path,
        store=store,
        symbol="AAPL",
        timeframe="1D",
        calendar_metadata=calendar_meta,
    )

    # 6. Assert the actual StoreResult contract.
    assert result.dataset_identity is not None
    assert result.dataset_sha256 is not None
    assert result.is_new is True

    # Canonical dataset identity/hash must not collapse into raw acquisition byte identity.
    assert result.dataset_sha256 != raw_acquisition_sha

    # 7. Inspect persisted manifest through the actual DatasetStore API.
    _, stored_manifest = store.retrieve(result.dataset_identity)

    assert stored_manifest["dataset_identity"] == result.dataset_identity
    assert stored_manifest["dataset_sha256"] == result.dataset_sha256
    assert stored_manifest["calendar_sha256"] == calendar_meta.sha256
