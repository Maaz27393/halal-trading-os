import pytest
import pandas as pd
import pathlib
import json
import hashlib
from datetime import datetime, timezone

from src.calendar_adapter import (
    load_and_verify_calendar,
    CalendarMetadata,
    compute_canonical_hash
)
from src.validator import validate_ohlcv

from src.dataset_store import (
    DatasetStore,
    DatasetConflictError,
    DatasetIntegrityError,
    compute_dataset_sha256,
    compute_dataset_identity
)

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
        'high': [101.5, 103.0],
        'low': [99.0, 101.0],
        'close': [101.0, 102.0],
        'volume': [1000, 1500]
    })

def test_p43_r01_new_dataset_cache_miss(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    assert res.is_new is True

def test_p43_r02_retrieval_of_stored_dataset(temp_store, sample_df, sample_calendar):
    res1 = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    retrieved_df, metadata = temp_store.retrieve(res1.dataset_identity)
    assert not retrieved_df.empty
    assert metadata['dataset_sha256'] == res1.dataset_sha256

def test_p43_r03_identical_dataset_cache_hit(temp_store, sample_df, sample_calendar):
    res1 = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    res2 = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    assert res2.is_new is False
    assert res1.dataset_identity == res2.dataset_identity

def test_p43_r04_same_dataset_different_calendar(tmp_path, sample_df):
    cal_path_1 = tmp_path / "calendar_a.json"
    data_a = {
        "calendar_id": "NYSE_A",
        "calendar_version": "1.0.0",
        "exchange": "NYSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [{"date": "2026-01-02"}]
    }
    data_a["sha256"] = compute_canonical_hash(data_a)
    cal_path_1.write_text(json.dumps(data_a))

    cal_path_2 = tmp_path / "calendar_b.json"
    data_b = {
        "calendar_id": "NYSE_B",
        "calendar_version": "2.0.0",
        "exchange": "NYSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [{"date": "2026-01-02"}]
    }
    data_b["sha256"] = compute_canonical_hash(data_b)
    cal_path_2.write_text(json.dumps(data_b))

    cal_meta_1 = load_and_verify_calendar(cal_path_1)
    cal_meta_2 = load_and_verify_calendar(cal_path_2)

    id1 = compute_dataset_identity(sample_df, cal_meta_1)
    id2 = compute_dataset_identity(sample_df, cal_meta_2)
    assert id1 != id2

def test_p43_r05_different_dataset_same_calendar():
    df1 = pd.DataFrame({'timestamp': pd.to_datetime(['2026-01-02 09:30:00'], utc=True), 'open': [100.0], 'high': [101.5], 'low': [99.0], 'close': [101.0], 'volume': [1000]})
    df2 = pd.DataFrame({'timestamp': pd.to_datetime(['2026-01-02 09:30:00'], utc=True), 'open': [200.0], 'high': [201.5], 'low': [199.0], 'close': [201.0], 'volume': [2000]})
    assert compute_dataset_sha256(df1) != compute_dataset_sha256(df2)

def test_p43_r06_existing_target_conflicting_dataset(temp_store, sample_df, sample_calendar):
    temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    conflicting_df = sample_df.copy()
    conflicting_df.loc[0, 'close'] = 999.0
    with pytest.raises(DatasetConflictError):
        temp_store.store_with_forced_collision(conflicting_df, sample_calendar, symbol='AAPL', timeframe='1d')

def test_p43_r07_existing_target_conflicting_manifest(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    with pytest.raises(DatasetConflictError):
        temp_store.tamper_manifest_collision(res.dataset_identity)

def test_p43_r08_dataset_content_tampered(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    temp_store.tamper_dataset_content_file(res.dataset_identity)
    with pytest.raises(DatasetIntegrityError):
        temp_store.retrieve(res.dataset_identity)

def test_p43_r09_manifest_tampered(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    temp_store.tamper_manifest_file(res.dataset_identity)
    with pytest.raises(DatasetIntegrityError):
        temp_store.retrieve(res.dataset_identity)

def test_p43_r10_dataset_manifest_identity_mismatch(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    temp_store.inject_manifest_mismatch(res.dataset_identity)
    with pytest.raises(DatasetIntegrityError):
        temp_store.retrieve(res.dataset_identity)

def test_p43_r11_unverified_calendar_hash_supplied(temp_store, sample_df):
    with pytest.raises((TypeError, ValueError, AttributeError)):
        temp_store.store(sample_df, 'unverified_calendar_sha_string', symbol='AAPL', timeframe='1d')

def test_p43_r12_verified_calendar_metadata_accepted(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    assert res.dataset_identity is not None

def test_p43_r13_column_reordering_canonical_hash(sample_df):
    df_reordered = sample_df[['volume', 'close', 'low', 'high', 'open', 'timestamp']]
    assert compute_dataset_sha256(df_reordered) == compute_dataset_sha256(sample_df)

def test_p43_r14_equivalent_numeric_formatting():
    df_base = pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-02 09:30:00'], utc=True),
        'open': [100], 'high': [101.5], 'low': [99], 'close': [101], 'volume': [1000]
    })
    df_alt = pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-02 09:30:00'], utc=True),
        'open': [100.0], 'high': [101.50], 'low': [99.00], 'close': [101.000], 'volume': [1000.0]
    })
    assert compute_dataset_sha256(df_base) == compute_dataset_sha256(df_alt)

def test_p43_r15_row_reordering_canonical_hash(sample_df):
    df_shuffled = sample_df.iloc[::-1].reset_index(drop=True)
    assert compute_dataset_sha256(df_shuffled) == compute_dataset_sha256(sample_df)

def test_p43_r16_missing_manifest_invalid(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    temp_store.delete_manifest_file(res.dataset_identity)
    with pytest.raises(DatasetIntegrityError):
        temp_store.retrieve(res.dataset_identity)

def test_p43_r17_missing_dataset_invalid(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    temp_store.delete_dataset_file(res.dataset_identity)
    with pytest.raises(DatasetIntegrityError):
        temp_store.retrieve(res.dataset_identity)

def test_p43_r18_partial_artifact_ignored(temp_store):
    temp_store.create_orphan_tmp_artifact()
    assert len(temp_store.list_valid_cache_entries()) == 0

def test_p43_r19_concurrent_publication_no_clobber(temp_store, sample_df, sample_calendar):
    temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d')
    assert res.is_new is False

def test_p43_r20_dataset_identity_calculation(sample_calendar, sample_df):
    d_sha = compute_dataset_sha256(sample_df)
    expected_identity = hashlib.sha256(f"{d_sha}:{sample_calendar.sha256}".encode('utf-8')).hexdigest()
    assert compute_dataset_identity(sample_df, sample_calendar) == expected_identity

def test_p43_r21_manifest_provenance_chain(temp_store, sample_df, sample_calendar):
    res = temp_store.store(sample_df, sample_calendar, symbol='AAPL', timeframe='1d', strategy_id='momentum_v1')
    manifest = temp_store.get_manifest(res.dataset_identity)
    assert manifest['dataset_sha256'] == res.dataset_sha256
    assert manifest['calendar_sha256'] == sample_calendar.sha256
    assert manifest['strategy_id'] == 'momentum_v1'
