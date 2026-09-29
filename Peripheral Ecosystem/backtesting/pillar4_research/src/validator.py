from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Any

import pandas as pd


REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


@dataclass
class ValidationIssue:
    code: str
    severity: str
    message: str
    count: int = 1


@dataclass
class ValidationResult:
    status: str
    source_file: str
    symbol: str
    timeframe: str
    row_count: int
    first_timestamp: str | None
    last_timestamp: str | None
    issues: list[ValidationIssue]
    source_sha256: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["issues"] = [asdict(i) for i in self.issues]
        return data


class DataValidationError(ValueError):
    pass


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_ohlcv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataValidationError(
            f"Missing required columns: {', '.join(missing)}"
        )

    result = df[REQUIRED_COLUMNS].copy()
    result["Date"] = pd.to_datetime(result["Date"], errors="coerce")

    for column in ["Open", "High", "Low", "Close", "Volume"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    return result


def validate_ohlcv(
    df: pd.DataFrame,
    source_file: Path,
    symbol: str,
    timeframe: str = "1D",
    trading_calendar: Iterable[pd.Timestamp] | None = None,
) -> ValidationResult:
    issues: list[ValidationIssue] = []

    null_counts = df[REQUIRED_COLUMNS].isna().sum()
    null_total = int(null_counts.sum())
    if null_total:
        issues.append(
            ValidationIssue(
                "NULL_VALUES",
                "ERROR",
                "Required OHLCV fields contain null/invalid values.",
                null_total,
            )
        )

    duplicate_dates = int(df["Date"].duplicated(keep=False).sum())
    if duplicate_dates:
        issues.append(
            ValidationIssue(
                "DUPLICATE_BARS",
                "ERROR",
                "Duplicate timestamps were found.",
                duplicate_dates,
            )
        )

    non_monotonic = int((df["Date"].diff().dropna() < pd.Timedelta(0)).sum())
    if non_monotonic:
        issues.append(
            ValidationIssue(
                "NON_CHRONOLOGICAL",
                "ERROR",
                "Bars are not chronologically sorted.",
                non_monotonic,
            )
        )

    valid_ohlc = df.dropna(subset=["Open", "High", "Low", "Close"])
    high_invalid = int(
        (valid_ohlc["High"] < valid_ohlc[["Open", "Close"]].max(axis=1)).sum()
    )
    low_invalid = int(
        (valid_ohlc["Low"] > valid_ohlc[["Open", "Close"]].min(axis=1)).sum()
    )
    range_invalid = int((valid_ohlc["High"] < valid_ohlc["Low"]).sum())

    if high_invalid:
        issues.append(
            ValidationIssue(
                "HIGH_INCONSISTENCY",
                "ERROR",
                "High is below Open or Close.",
                high_invalid,
            )
        )
    if low_invalid:
        issues.append(
            ValidationIssue(
                "LOW_INCONSISTENCY",
                "ERROR",
                "Low is above Open or Close.",
                low_invalid,
            )
        )
    if range_invalid:
        issues.append(
            ValidationIssue(
                "RANGE_INCONSISTENCY",
                "ERROR",
                "High is below Low.",
                range_invalid,
            )
        )

    negative_volume = int((df["Volume"].dropna() < 0).sum())
    if negative_volume:
        issues.append(
            ValidationIssue(
                "NEGATIVE_VOLUME",
                "ERROR",
                "Volume contains negative values.",
                negative_volume,
            )
        )

    zero_or_negative_prices = int(
        (
            valid_ohlc[["Open", "High", "Low", "Close"]]
            .le(0)
            .any(axis=1)
        ).sum()
    )
    if zero_or_negative_prices:
        issues.append(
            ValidationIssue(
                "NON_POSITIVE_PRICE",
                "ERROR",
                "OHLC contains zero or negative prices.",
                zero_or_negative_prices,
            )
        )

    if trading_calendar is not None and not df["Date"].isna().any():
        actual = pd.DatetimeIndex(df["Date"].dt.normalize().unique())
        expected = pd.DatetimeIndex(
            pd.to_datetime(list(trading_calendar)).normalize().unique()
        )
        missing = expected.difference(actual)
        unexpected = actual.difference(expected)

        if len(missing):
            issues.append(
                ValidationIssue(
                    "MISSING_CALENDAR_BARS",
                    "ERROR",
                    "Expected trading-calendar dates are absent.",
                    len(missing),
                )
            )
        if len(unexpected):
            issues.append(
                ValidationIssue(
                    "UNEXPECTED_CALENDAR_BARS",
                    "WARNING",
                    "Dataset contains dates not present in the supplied calendar.",
                    len(unexpected),
                )
            )
    elif len(df) > 1 and not df["Date"].isna().any():
        deltas = df["Date"].sort_values().diff().dropna()
        suspicious = int((deltas > pd.Timedelta(days=3)).sum())
        if suspicious:
            issues.append(
                ValidationIssue(
                    "UNVERIFIED_DATE_GAPS",
                    "WARNING",
                    "Date gaps exist, but exact missing-session validation requires a trading calendar.",
                    suspicious,
                )
            )

    has_error = any(issue.severity == "ERROR" for issue in issues)
    status = "BLOCKED" if has_error else "PASSED_WITH_WARNINGS" if issues else "PASSED"

    first_timestamp = None
    last_timestamp = None
    if not df["Date"].dropna().empty:
        first_timestamp = df["Date"].min().isoformat()
        last_timestamp = df["Date"].max().isoformat()

    return ValidationResult(
        status=status,
        source_file=str(source_file),
        symbol=symbol,
        timeframe=timeframe,
        row_count=len(df),
        first_timestamp=first_timestamp,
        last_timestamp=last_timestamp,
        issues=issues,
        source_sha256=sha256_file(source_file),
    )


def write_manifest(result: ValidationResult, destination: Path, calendar_metadata: Any | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "manifest_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": result.to_dict(),
        "research_use": "BLOCKED" if result.status == "BLOCKED" else "ELIGIBLE_PENDING_REVIEW",
        "operational_authority": "NONE",
    }
    if calendar_metadata is not None:
        payload["calendar"] = {
            "calendar_id": calendar_metadata.calendar_id,
            "calendar_version": calendar_metadata.calendar_version,
            "calendar_sha256": calendar_metadata.sha256,
        }
    destination.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
