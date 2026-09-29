from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CalendarValidationError(ValueError):
    """Raised when a calendar artifact fails structural or schema validation."""
    pass


@dataclass(frozen=True)
class CalendarMetadata:
    calendar_id: str
    calendar_version: str
    exchange: str
    market: str
    effective_from: str
    effective_to: str
    sessions: frozenset[str]
    sha256: str


def compute_canonical_hash(payload: dict[str, Any]) -> str:
    """Computes SHA-256 over canonical JSON payload excluding hash fingerprint fields."""
    clean_payload = {k: v for k, v in payload.items() if k not in ("sha256", "calendar_sha256")}
    canonical_str = json.dumps(clean_payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


def load_and_verify_calendar(calendar_path: str | Path) -> CalendarMetadata:
    """
    Loads a versioned local calendar artifact, verifies its SHA-256 integrity,
    validates its schema, and returns immutable parsed metadata.
    """
    p = Path(calendar_path)
    if not p.exists():
        raise FileNotFoundError(f"Calendar artifact not found at: {p}")

    try:
        raw_data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        if isinstance(e, FileNotFoundError):
            raise
        raise CalendarValidationError(f"Failed to parse calendar JSON: {e}")

    if not isinstance(raw_data, dict):
        raise CalendarValidationError("Calendar root must be a JSON object.")

    # 1. Mandatory hash presence check
    provided_hash = raw_data.get("sha256") or raw_data.get("calendar_sha256")
    if not provided_hash:
        raise ValueError("Calendar artifact is missing mandatory 'sha256' or 'calendar_sha256' fingerprint.")

    # 2. Cryptographic integrity verification
    computed_hash = compute_canonical_hash(raw_data)
    if computed_hash != provided_hash:
        raise ValueError(
            f"Calendar integrity violation! Computed hash {computed_hash} does not match provided hash {provided_hash}."
        )

    # 3. Mandatory metadata validation
    required_fields = [
        "calendar_id",
        "calendar_version",
        "exchange",
        "market",
        "effective_from",
        "effective_to",
        "sessions",
    ]
    for field in required_fields:
        if field not in raw_data:
            raise CalendarValidationError(f"Missing required calendar metadata field: '{field}'")

    if not isinstance(raw_data["sessions"], list):
        raise CalendarValidationError("Calendar 'sessions' must be a list.")

    session_dates = set()
    for idx, s in enumerate(raw_data["sessions"]):
        if not isinstance(s, dict) or "date" not in s:
            raise CalendarValidationError(
                f"Invalid session entry at index {idx}: must be an object containing 'date'."
            )
        session_dates.add(s["date"])

    return CalendarMetadata(
        calendar_id=raw_data["calendar_id"],
        calendar_version=raw_data["calendar_version"],
        exchange=raw_data["exchange"],
        market=raw_data["market"],
        effective_from=raw_data["effective_from"],
        effective_to=raw_data["effective_to"],
        sessions=frozenset(session_dates),
        sha256=computed_hash,
    )
