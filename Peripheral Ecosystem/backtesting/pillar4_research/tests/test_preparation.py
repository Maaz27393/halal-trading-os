from __future__ import annotations

import pytest
import pandas as pd
import json
from pathlib import Path
from src.validator import validate_ohlcv, load_ohlcv, DataValidationError
from src.dataset_store import DatasetStore, compute_dataset_identity
from src.calendar_adapter import CalendarMetadata, compute_canonical_hash, load_and_verify_calendar
from src.dataset_preparation import prepare_dataset, DatasetPreparationError

def test_preparation_valid_csv(tmp_path):
    csv_path = tmp_path / "raw_sample.csv"
    csv_path.write_text(
        "Date,Open,High,Low,Close,Volume\n"
        "2025-01-02,100.0,105.0,98.0,103.0,1000\n"
        "2025-01-03,103.0,107.0,101.0,106.0,1500\n"
    )
    
    df = load_ohlcv(csv_path)
    assert not df.empty
    assert list(df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]

def test_preparation_missing_column_blocks(tmp_path):
    csv_path = tmp_path / "bad_sample.csv"
    csv_path.write_text(
        "Date,Open,High,Close,Volume\n"
        "2025-01-02,100.0,105.0,103.0,1000\n"
    )
    with pytest.raises(DataValidationError, match="Missing required columns"):
        load_ohlcv(csv_path)

def test_preparation_semantic_validation_blocks(tmp_path):
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text("dummy content")
    
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2025-01-02", "2025-01-03"]),
        "Open": [100.0, 103.0],
        "High": [95.0, 107.0],  # High below Open -> ERROR
        "Low": [98.0, 101.0],
        "Close": [103.0, 106.0],
        "Volume": [1000, 1500]
    })
    res = validate_ohlcv(df, csv_path, symbol="TEST:SYMBOL", timeframe="1D")
    assert res.status == "BLOCKED"
    assert any(issue.code == "HIGH_INCONSISTENCY" for issue in res.issues)

def test_duplicate_timestamps_blocks(tmp_path):
    csv_path = tmp_path / "dups.csv"
    csv_path.write_text("dummy")
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2025-01-02", "2025-01-02"]),
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [98.0, 99.0],
        "Close": [103.0, 104.0],
        "Volume": [1000, 1100]
    })
    res = validate_ohlcv(df, csv_path, symbol="TEST:SYMBOL", timeframe="1D")
    assert res.status == "BLOCKED"
    assert any(issue.code == "DUPLICATE_BARS" for issue in res.issues)

def test_negative_volume_blocks(tmp_path):
    csv_path = tmp_path / "neg_vol.csv"
    csv_path.write_text("dummy")
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2025-01-02"]),
        "Open": [100.0],
        "High": [105.0],
        "Low": [98.0],
        "Close": [103.0],
        "Volume": [-500]
    })
    res = validate_ohlcv(df, csv_path, symbol="TEST:SYMBOL", timeframe="1D")
    assert res.status == "BLOCKED"
    assert any(issue.code == "NEGATIVE_VOLUME" for issue in res.issues)

def test_calendar_binding_validation(tmp_path):
    csv_path = tmp_path / "cal_test.csv"
    csv_path.write_text("dummy")
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2025-01-02"]),
        "Open": [100.0],
        "High": [105.0],
        "Low": [98.0],
        "Close": [103.0],
        "Volume": [1000]
    })
    calendar_timestamps = [pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-03")]
    res = validate_ohlcv(df, csv_path, symbol="TEST:SYMBOL", timeframe="1D", trading_calendar=calendar_timestamps)
    assert res.status == "BLOCKED"
    assert any(issue.code == "MISSING_CALENDAR_BARS" for issue in res.issues)

def test_unexpected_calendar_session_is_warning(tmp_path):
    csv_path = tmp_path / "cal_test.csv"
    csv_path.write_text("dummy")
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2025-01-02", "2025-01-03"]),
        "Open": [100.0, 103.0],
        "High": [105.0, 107.0],
        "Low": [98.0, 101.0],
        "Close": [103.0, 106.0],
        "Volume": [1000, 1500]
    })
    calendar_timestamps = [pd.Timestamp("2025-01-02")]
    res = validate_ohlcv(df, csv_path, symbol="TEST:SYMBOL", timeframe="1D", trading_calendar=calendar_timestamps)
    assert res.status == "PASSED_WITH_WARNINGS"
    assert any(issue.code == "UNEXPECTED_CALENDAR_BARS" for issue in res.issues)

def test_storage_boundary_invariant(tmp_path):
    store = DatasetStore(tmp_path / "store")
    
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text(
        "Date,Open,High,Low,Close,Volume\n"
        "2025-01-02,100.0,90.0,98.0,103.0,1000\n"
    )
    
    cal_json = {
        "calendar_id": "test_cal",
        "calendar_version": "1.0",
        "exchange": "TEST",
        "market": "EQUITY",
        "effective_from": "2025-01-01",
        "effective_to": "2025-12-31",
        "sessions": [
            {"date": "2025-01-02"}
        ]
    }
    cal_json["sha256"] = compute_canonical_hash(cal_json)
    
    cal_file = tmp_path / "cal.json"
    cal_file.write_text(json.dumps(cal_json), encoding="utf-8")
    cal_meta = load_and_verify_calendar(cal_file)
    
    with pytest.raises(DatasetPreparationError):
        prepare_dataset(csv_path, store, symbol="TEST:SYMBOL", timeframe="1D", calendar_metadata=cal_meta)

def test_storage_warning_boundary_blocks(tmp_path):
    store = DatasetStore(tmp_path / "store")
    
    csv_path = tmp_path / "warn.csv"
    csv_path.write_text(
        "Date,Open,High,Low,Close,Volume\n"
        "2025-01-02,100.0,105.0,98.0,103.0,1000\n"
        "2025-01-03,103.0,107.0,101.0,106.0,1500\n"
    )
    
    cal_json = {
        "calendar_id": "test_cal",
        "calendar_version": "1.0",
        "exchange": "TEST",
        "market": "EQUITY",
        "effective_from": "2025-01-01",
        "effective_to": "2025-12-31",
        "sessions": [
            {"date": "2025-01-02"}
        ]
    }
    cal_json["sha256"] = compute_canonical_hash(cal_json)
    
    cal_file = tmp_path / "cal.json"
    cal_file.write_text(json.dumps(cal_json), encoding="utf-8")
    cal_meta = load_and_verify_calendar(cal_file)
    
    # Expect warnings to block preparation by default (fail closed)
    with pytest.raises(DatasetPreparationError, match="WARNING"):
        prepare_dataset(csv_path, store, symbol="TEST:SYMBOL", timeframe="1D", calendar_metadata=cal_meta)
