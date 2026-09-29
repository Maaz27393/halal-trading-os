from __future__ import annotations

import json
from pathlib import Path
import pytest
import sys

# Ensure src is in python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calendar_adapter import (
    load_and_verify_calendar,
    compute_canonical_hash,
    CalendarValidationError,
)


@pytest.fixture
def valid_calendar_dict():
    return {
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


def test_valid_calendar_loads_successfully(tmp_path, valid_calendar_dict):
    valid_calendar_dict["sha256"] = compute_canonical_hash(valid_calendar_dict)
    
    cal_file = tmp_path / "calendar.json"
    cal_file.write_text(json.dumps(valid_calendar_dict), encoding="utf-8")

    meta = load_and_verify_calendar(cal_file)
    assert meta.calendar_id == "NSE_EQUITY_2026"
    assert meta.calendar_version == "NSE_CALENDAR_2026_V1"
    assert "2026-01-02" in meta.sessions
    assert "2026-01-05" in meta.sessions
    assert meta.sha256 == valid_calendar_dict["sha256"]


def test_canonical_hash_excludes_sha256(valid_calendar_dict):
    dict_without_hash = valid_calendar_dict.copy()
    hash1 = compute_canonical_hash(dict_without_hash)

    dict_with_hash = valid_calendar_dict.copy()
    dict_with_hash["sha256"] = "deadbeef" * 8
    hash2 = compute_canonical_hash(dict_with_hash)

    assert hash1 == hash2, "Hash must exclude sha256 field to prevent self-reference paradox"


def test_canonicalization_is_deterministic(valid_calendar_dict):
    reordered = {
        "market": valid_calendar_dict["market"],
        "calendar_version": valid_calendar_dict["calendar_version"],
        "sessions": valid_calendar_dict["sessions"],
        "effective_to": valid_calendar_dict["effective_to"],
        "exchange": valid_calendar_dict["exchange"],
        "calendar_id": valid_calendar_dict["calendar_id"],
        "effective_from": valid_calendar_dict["effective_from"],
    }
    assert compute_canonical_hash(valid_calendar_dict) == compute_canonical_hash(reordered)


def test_tampered_payload_is_rejected(tmp_path, valid_calendar_dict):
    valid_calendar_dict["sha256"] = compute_canonical_hash(valid_calendar_dict)
    valid_calendar_dict["sessions"].append({"date": "2026-01-06", "session_open": "09:15:00", "session_close": "15:30:00"})

    cal_file = tmp_path / "tampered_calendar.json"
    cal_file.write_text(json.dumps(valid_calendar_dict), encoding="utf-8")

    try:
        load_and_verify_calendar(cal_file)
        raise AssertionError("Should have failed on tampered payload")
    except ValueError as e:
        assert "integrity violation" in str(e)


def test_missing_hash_is_rejected(tmp_path, valid_calendar_dict):
    cal_file = tmp_path / "no_hash_calendar.json"
    cal_file.write_text(json.dumps(valid_calendar_dict), encoding="utf-8")

    try:
        load_and_verify_calendar(cal_file)
        raise AssertionError("Should have failed on missing hash")
    except ValueError as e:
        assert "missing mandatory 'sha256'" in str(e)


def test_missing_required_metadata_fails_closed(tmp_path):
    incomplete_dict = {
        "calendar_id": "NSE_EQUITY_2026",
        "sessions": []
    }
    incomplete_dict["sha256"] = compute_canonical_hash(incomplete_dict)

    cal_file = tmp_path / "incomplete.json"
    cal_file.write_text(json.dumps(incomplete_dict), encoding="utf-8")

    try:
        load_and_verify_calendar(cal_file)
        raise AssertionError("Should have failed on incomplete metadata")
    except CalendarValidationError as e:
        assert "Missing required calendar metadata" in str(e)


def test_malformed_session_entries_fail_closed(tmp_path, valid_calendar_dict):
    valid_calendar_dict["sessions"] = [{"session_open": "09:15:00", "session_close": "15:30:00"}]
    valid_calendar_dict["sha256"] = compute_canonical_hash(valid_calendar_dict)

    cal_file = tmp_path / "malformed_session.json"
    cal_file.write_text(json.dumps(valid_calendar_dict), encoding="utf-8")

    try:
        load_and_verify_calendar(cal_file)
        raise AssertionError("Should have failed on malformed session")
    except CalendarValidationError as e:
        assert "Invalid session entry" in str(e)
