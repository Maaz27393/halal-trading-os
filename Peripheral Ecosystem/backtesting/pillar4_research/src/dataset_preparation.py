from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.calendar_adapter import CalendarMetadata
from src.dataset_store import DatasetStore, StoreResult
from src.validator import ValidationResult, load_ohlcv, validate_ohlcv


class DatasetPreparationError(ValueError):
    """Raised when dataset preparation or validation is blocked."""
    pass


def prepare_dataset(
    csv_path: Path | str,
    store: DatasetStore,
    symbol: str = "UNKNOWN",
    timeframe: str = "1D",
    calendar_metadata: CalendarMetadata | None = None,
    strategy_id: str | None = None,
) -> StoreResult:
    """
    Execute the P4.3 raw-data preparation boundary.

    Flow:
        raw CSV
          -> load/parse
          -> semantic + calendar validation
          -> BLOCKED or normalized
          -> DatasetStore

    Only a verified CalendarMetadata instance and a non-BLOCKED dataset
    may cross into DatasetStore.
    """
    csv_path = Path(csv_path)

    if not isinstance(calendar_metadata, CalendarMetadata):
        raise DatasetPreparationError(
            "Verified CalendarMetadata is required for dataset preparation."
        )

    # P4.3 calendar/session binding.
    trading_calendar = [
        pd.Timestamp(session).normalize()
        for session in calendar_metadata.sessions
    ]

    # 1. Load raw source-format OHLCV.
    try:
        df = load_ohlcv(csv_path)
    except Exception as exc:
        raise DatasetPreparationError(
            f"Failed to load raw OHLCV dataset: {exc}"
        ) from exc

    # 2. Validate semantic and calendar integrity.
    validation_result: ValidationResult = validate_ohlcv(
        df=df,
        source_file=csv_path,
        symbol=symbol,
        timeframe=timeframe,
        trading_calendar=trading_calendar,
    )

    # 3. Fail closed on anything other than strict PASSED (including warnings).
    if validation_result.status != "PASSED":
        blocking_messages = "; ".join(
            f"{issue.severity}: {issue.code}: {issue.message}"
            for issue in validation_result.issues
        )
        raise DatasetPreparationError(
            f"Dataset preparation {validation_result.status}: "
            f"{blocking_messages}"
        )

    # 4. Normalize P4.3 source schema to DatasetStore schema.
    df_normalized = df.rename(
        columns={
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    ).copy()

    df_normalized["timestamp"] = pd.to_datetime(
        df_normalized["timestamp"],
        utc=True,
    )

    # 5. Persist only validated canonical data.
    return store.store(
        df=df_normalized,
        calendar_metadata=calendar_metadata,
        symbol=symbol,
        timeframe=timeframe,
        strategy_id=strategy_id,
    )
