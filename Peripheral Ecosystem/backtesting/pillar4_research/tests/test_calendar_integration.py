from __future__ import annotations

import json
from pathlib import Path
import pytest
import pandas as pd
import sys

src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from calendar_adapter import (
    load_and_verify_calendar,
    compute_canonical_hash,
)
from validator import load_ohlcv, validate_ohlcv, write_manifest


@pytest.fixture
def sample_ohlcv_file(tmp_path):
    rows = [
        {"Date": "2026-01-02", "Open": 100, "High": 110, "Low": 95, "Close": 105, "Volume": 1000},
        {"Date": "2026-01-05", "Open": 105, "High": 112, "Low": 101, "Close": 110, "Volume": 1200},
    ]
    path = tmp_path / "NSE_EQUITY_TEST.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


@pytest.fixture
def valid_calendar_artifact(tmp_path):
    cal_dict = {
        "calendar_id": "NSE_EQUITY_2026",
        "calendar_version": "NSE_CALENDAR_2026_V1",
        "exchange": "NSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [
            {"date": "2026-01-02", "session_open": "09:15:00", "session_close": "15:30:00"},
            {"date": "2026-01-05", "session_open": "09:15:00", "session_close": "15:30:00"}
        ]
    }
    cal_dict["sha256"] = compute_canonical_hash(cal_dict)
    cal_path = tmp_path / "NSE_CALENDAR_2026_V1.json"
    cal_path.write_text(json.dumps(cal_dict), encoding="utf-8")
    return cal_path


def test_verified_calendar_integration_passes(sample_ohlcv_file, valid_calendar_artifact):
    metadata = load_and_verify_calendar(valid_calendar_artifact)
    assert metadata.sha256 is not None

    calendar_timestamps = pd.to_datetime(list(metadata.sessions))

    df = load_ohlcv(sample_ohlcv_file)
    result = validate_ohlcv(df, sample_ohlcv_file, "NSE:RELIANCE", trading_calendar=calendar_timestamps)

    assert result.status == "PASSED"
    assert result.row_count == 2
    assert not any(i.code == "MISSING_CALENDAR_BARS" for i in result.issues)


def test_dataset_missing_calendar_session_blocks(sample_ohlcv_file, tmp_path):
    cal_dict = {
        "calendar_id": "NSE_EQUITY_2026",
        "calendar_version": "NSE_CALENDAR_2026_V1",
        "exchange": "NSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [
            {"date": "2026-01-02", "session_open": "09:15:00", "session_close": "15:30:00"},
            {"date": "2026-01-05", "session_open": "09:15:00", "session_close": "15:30:00"},
            {"date": "2026-01-06", "session_open": "09:15:00", "session_close": "15:30:00"}
        ]
    }
    cal_dict["sha256"] = compute_canonical_hash(cal_dict)
    cal_path = tmp_path / "cal_with_gap.json"
    cal_path.write_text(json.dumps(cal_dict), encoding="utf-8")

    metadata = load_and_verify_calendar(cal_path)
    calendar_timestamps = pd.to_datetime(list(metadata.sessions))

    df = load_ohlcv(sample_ohlcv_file)
    result = validate_ohlcv(df, sample_ohlcv_file, "NSE:RELIANCE", trading_calendar=calendar_timestamps)

    assert result.status == "BLOCKED"
    issue = next(i for i in result.issues if i.code == "MISSING_CALENDAR_BARS")
    assert issue.count == 1


def test_tampered_calendar_artifact_refuses_entry(tmp_path):
    cal_dict = {
        "calendar_id": "NSE_EQUITY_2026",
        "calendar_version": "NSE_CALENDAR_2026_V1",
        "exchange": "NSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [{"date": "2026-01-02", "session_open": "09:15:00", "session_close": "15:30:00"}]
    }
    cal_dict["sha256"] = compute_canonical_hash(cal_dict)
    
    cal_dict["sessions"].append({"date": "2026-01-03", "session_open": "09:15:00", "session_close": "15:30:00"})
    
    tampered_path = tmp_path / "tampered.json"
    tampered_path.write_text(json.dumps(cal_dict), encoding="utf-8")

    with pytest.raises(ValueError, match="integrity violation"):
        load_and_verify_calendar(tampered_path)


def test_manifest_linkage_contains_calendar_identity(sample_ohlcv_file, valid_calendar_artifact, tmp_path):
    metadata = load_and_verify_calendar(valid_calendar_artifact)
    calendar_timestamps = pd.to_datetime(list(metadata.sessions))

    df = load_ohlcv(sample_ohlcv_file)
    result = validate_ohlcv(df, sample_ohlcv_file, "NSE:RELIANCE", trading_calendar=calendar_timestamps)

    manifest_path = tmp_path / "dataset_manifest.json"
    write_manifest(result, manifest_path, calendar_metadata=metadata)

    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    
    assert "calendar" in manifest_data
    assert manifest_data["calendar"]["calendar_id"] == "NSE_EQUITY_2026"
    assert manifest_data["calendar"]["calendar_version"] == "NSE_CALENDAR_2026_V1"
    assert manifest_data["calendar"]["calendar_sha256"] == metadata.sha256
