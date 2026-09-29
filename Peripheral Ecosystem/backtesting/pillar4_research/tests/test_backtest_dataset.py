from __future__ import annotations

import pytest
import pandas as pd
from src.calendar_adapter import load_and_verify_calendar, compute_canonical_hash
from src.dataset_store import DatasetStore
from src.dataset_loader import load_backtest_dataset
from src.backtest_dataset import BacktestDataset, DatasetMutationError

@pytest.fixture
def temp_store(tmp_path):
    return DatasetStore(tmp_path)

@pytest.fixture
def sample_calendar(tmp_path):
    cal_path = tmp_path / "valid_calendar.json"
    cal_data = {
        "calendar_id": "NYSE_DEFAULT",
        "calendar_version": "1.0.0",
        "exchange": "NYSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [{"date": "2026-01-02"}]
    }
    cal_data["sha256"] = compute_canonical_hash(cal_data)
    cal_path.write_text(str(cal_data).replace("'", '"'), encoding="utf-8")
    return load_and_verify_calendar(cal_path)

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-02 09:30:00'], utc=True),
        'open': [100.0],
        'high': [105.0],
        'low': [99.0],
        'close': [104.0],
        'volume': [1000]
    })

@pytest.fixture
def loaded_dataset(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol="AAPL", timeframe="1d")
    return load_backtest_dataset(temp_store, res.dataset_identity, sample_calendar)

def test_R09_provenance_metadata_present(loaded_dataset):
    """R09: BacktestDataset preserves complete cryptographic provenance metadata."""
    assert loaded_dataset.dataset_identity is not None
    assert loaded_dataset.dataset_sha256 is not None
    assert loaded_dataset.calendar_sha256 is not None
    assert loaded_dataset.calendar_metadata is not None

def test_R10_normalized_ohlcv_contract(loaded_dataset):
    """R10: BacktestDataset enforces normalized OHLCV structural contracts."""
    df = loaded_dataset.df
    expected_cols = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
    assert expected_cols.issubset(df.columns)
    assert pd.api.types.is_datetime64_any_dtype(df['timestamp'])

def test_R11_verified_dataset_immutable_mutation_rejected(loaded_dataset):
    """R11: Verified BacktestDataset cannot be silently mutated downstream."""
    with pytest.raises((DatasetMutationError, TypeError, AttributeError)):
        loaded_dataset.df['close'] = loaded_dataset.df['close'] * 2.0
