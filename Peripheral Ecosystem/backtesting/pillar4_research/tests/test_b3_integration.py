from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from historical_acquisition.yfinance_adapter import YFinanceDataSource
from historical_acquisition.qualification import (
    QualificationManager,
)
from src.calendar_adapter import load_and_verify_calendar
from src.dataset_preparation import prepare_dataset, DatasetPreparationError
from src.dataset_store import DatasetStore


BASE_DIR = Path(__file__).resolve().parents[1]
CALENDAR_PATH = BASE_DIR / "tests" / "fixtures" / "calendars" / "valid_calendar.json"


def _provider_fixture():
    return pd.DataFrame(
        {
            "Open": [100.0, 105.0],
            "High": [110.0, 112.0],
            "Low": [95.0, 101.0],
            "Close": [105.0, 110.0],
            "Volume": [1000, 1200],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-05"]),
    )


def _adapter():
    return YFinanceDataSource(
        downloader=lambda *args, **kwargs: _provider_fixture()
    )


def test_b3_provider_raw_bytes_can_be_staged_exactly(tmp_path):
    """
    RED contract:

    The staging boundary must persist HistoricalBars.raw_csv_bytes exactly,
    without reconstructing or transforming the DataFrame.
    """
    from historical_acquisition.staging import stage_raw_bars

    bars = _adapter().fetch_daily(
        "NSE:RELIANCE",
        "2026-01-02",
        "2026-01-05",
    )

    staged_path = stage_raw_bars(
        bars=bars,
        staging_dir=tmp_path,
    )

    assert staged_path.exists()

    persisted_bytes = staged_path.read_bytes()

    assert persisted_bytes == bars.raw_csv_bytes
    assert hashlib.sha256(persisted_bytes).hexdigest() == (
        hashlib.sha256(bars.raw_csv_bytes).hexdigest()
    )


def test_b3_staged_raw_artifact_qualifies_then_crosses_p43_boundary(tmp_path):
    """
    Integration contract:

    provider -> exact raw staging -> qualification metadata -> verified
    calendar -> frozen P4.3 preparation/storage boundary.
    """
    from historical_acquisition.staging import stage_raw_bars

    bars = _adapter().fetch_daily(
        "NSE:RELIANCE",
        "2026-01-02",
        "2026-01-05",
    )

    staged_path = stage_raw_bars(
        bars=bars,
        staging_dir=tmp_path / "staging",
    )

    calendar_metadata = load_and_verify_calendar(CALENDAR_PATH)

    manifest = QualificationManager.generate_manifest(
        csv_path=staged_path,
        source_identity="RELIANCE_1D_RAW",
        provider=bars.provider,
        symbol=bars.symbol,
        timeframe=bars.timeframe,
        requested_start=bars.start_date,
        requested_end=bars.end_date,
        adjustment_status=bars.adjustment_status,
        calendar_identity=calendar_metadata.calendar_id,
        calendar_sha256=calendar_metadata.sha256,
    )

    assert manifest.raw_sha256 == hashlib.sha256(
        staged_path.read_bytes()
    ).hexdigest()

    assert manifest.row_count == 2
    assert manifest.actual_first_date == "2026-01-02"
    assert manifest.actual_last_date == "2026-01-05"
    assert manifest.adjustment_status == "RAW_UNADJUSTED"
    assert manifest.calendar_identity == calendar_metadata.calendar_id
    assert manifest.calendar_sha256 == calendar_metadata.sha256

    store = DatasetStore(tmp_path / "store")

    result = prepare_dataset(
        staged_path,
        store,
        symbol="NSE:RELIANCE",
        timeframe="1D",
        calendar_metadata=calendar_metadata,
    )

    assert result.is_new is True
    assert result.dataset_sha256
    assert result.dataset_identity

    assert result.dataset_sha256 != manifest.raw_sha256

    _, stored_manifest = store.retrieve(result.dataset_identity)

    assert stored_manifest["dataset_identity"] == result.dataset_identity
    assert stored_manifest["dataset_sha256"] == result.dataset_sha256
    assert stored_manifest["calendar_sha256"] == calendar_metadata.sha256


def test_b3_calendar_mismatch_fails_closed(tmp_path):
    """
    The provider artifact must not bypass P4.3 calendar validation.

    A verified calendar that does not contain every staged trading session
    must prevent DatasetStore entry.
    """
    from historical_acquisition.staging import stage_raw_bars

    bars = _adapter().fetch_daily(
        "NSE:RELIANCE",
        "2026-01-02",
        "2026-01-05",
    )

    staged_path = stage_raw_bars(
        bars=bars,
        staging_dir=tmp_path / "staging",
    )

    mismatched_calendar = {
        "calendar_id": "NSE_EQUITY_2026_MISMATCH",
        "calendar_version": "NSE_CALENDAR_2026_TEST",
        "exchange": "NSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [
            {
                "date": "2026-01-02",
                "session_open": "09:15:00",
                "session_close": "15:30:00",
            }
        ],
    }

    from src.calendar_adapter import compute_canonical_hash

    mismatched_calendar["sha256"] = compute_canonical_hash(
        mismatched_calendar
    )

    calendar_path = tmp_path / "mismatched_calendar.json"
    calendar_path.write_text(
        json.dumps(mismatched_calendar),
        encoding="utf-8",
    )

    calendar_metadata = load_and_verify_calendar(calendar_path)

    store = DatasetStore(tmp_path / "store")

    with pytest.raises(DatasetPreparationError):
        prepare_dataset(
            staged_path,
            store,
            symbol="NSE:RELIANCE",
            timeframe="1D",
            calendar_metadata=calendar_metadata,
        )
