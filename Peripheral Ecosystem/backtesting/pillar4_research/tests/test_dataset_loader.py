from __future__ import annotations

import pytest
import pandas as pd
import pathlib
import json

from src.calendar_adapter import load_and_verify_calendar, compute_canonical_hash, CalendarMetadata
from src.dataset_store import DatasetStore, DatasetIntegrityError
from src.dataset_loader import load_backtest_dataset, BacktestDataset, DatasetLoaderError

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
        "sessions": [
            {"date": "2026-01-02"},
            {"date": "2026-01-05"}
        ]
    }
    cal_data["sha256"] = compute_canonical_hash(cal_data)
    cal_path.write_text(json.dumps(cal_data, indent=2), encoding="utf-8")
    return load_and_verify_calendar(cal_path)

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-02 09:30:00', '2026-01-05 09:30:00'], utc=True),
        'open': [100.0, 102.5],
        'high': [105.0, 106.0],
        'low': [99.0, 101.0],
        'close': [104.0, 105.5],
        'volume': [1000, 1500]
    })

@pytest.fixture
def stored_dataset(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol="AAPL", timeframe="1d")
    return res.dataset_identity

def test_R01_valid_dataset_loads(temp_store, stored_dataset, sample_calendar):
    dataset = load_backtest_dataset(temp_store, stored_dataset, sample_calendar)
    assert isinstance(dataset, BacktestDataset)
    assert dataset.dataset_identity == stored_dataset
    assert not dataset.df.empty

def test_R02_nonexistent_dataset_rejected(temp_store, sample_calendar):
    with pytest.raises((DatasetIntegrityError, DatasetLoaderError)):
        load_backtest_dataset(temp_store, "nonexistent_identity_hash_abc123", sample_calendar)

def test_R03_manifest_removal_rejected(temp_store, stored_dataset, sample_calendar):
    temp_store.delete_manifest_file(stored_dataset)
    with pytest.raises((DatasetIntegrityError, DatasetLoaderError)):
        load_backtest_dataset(temp_store, stored_dataset, sample_calendar)

def test_R04_tampered_dataset_rejected(temp_store, stored_dataset, sample_calendar):
    temp_store.tamper_dataset_content_file(stored_dataset)
    with pytest.raises((DatasetIntegrityError, DatasetLoaderError)):
        load_backtest_dataset(temp_store, stored_dataset, sample_calendar)

def test_R05_tampered_manifest_rejected(temp_store, stored_dataset, sample_calendar):
    temp_store.tamper_manifest_file(stored_dataset)
    with pytest.raises((DatasetIntegrityError, DatasetLoaderError)):
        load_backtest_dataset(temp_store, stored_dataset, sample_calendar)

def test_R06_manifest_mismatch_rejected(temp_store, stored_dataset, sample_calendar):
    temp_store.inject_manifest_mismatch(stored_dataset)
    with pytest.raises((DatasetIntegrityError, DatasetLoaderError)):
        load_backtest_dataset(temp_store, stored_dataset, sample_calendar)

def test_R07_different_verified_calendar_rejected(temp_store, stored_dataset, tmp_path, sample_df):
    cal_path = tmp_path / "other_calendar.json"
    cal_data = {
        "calendar_id": "NYSE_OTHER",
        "calendar_version": "1.0.0",
        "exchange": "NYSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [{"date": "2026-01-03"}]
    }
    cal_data["sha256"] = compute_canonical_hash(cal_data)
    cal_path.write_text(json.dumps(cal_data, indent=2), encoding="utf-8")
    other_calendar = load_and_verify_calendar(cal_path)

    with pytest.raises((DatasetIntegrityError, DatasetLoaderError)):
        load_backtest_dataset(temp_store, stored_dataset, other_calendar)

def test_R08_raw_unverified_calendar_rejected(temp_store, stored_dataset):
    with pytest.raises((TypeError, DatasetLoaderError)):
        load_backtest_dataset(temp_store, stored_dataset, "2a30779557c0b120a24329e78a32cc237580aa27c027bca6abda2560685226a6")
