from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd

from .contracts import (
    RawAcquisitionRequest,
    RawAcquisitionResult,
    RawMetadata,
    RawProvenance,
)
from .source import HistoricalDataSource
from .yfinance_adapter import YFinanceDataSource


DEFAULT_PROVIDER_ADAPTER_VERSION = "1.0.0"


def _normalize_actual_date(value: object) -> str:
    """
    Convert a provider DataFrame date-like value to canonical YYYY-MM-DD.

    Handles datetime objects, timestamps, and string representations
    that may contain time or timezone offsets (e.g. '2026-01-02 00:00:00-05:00').
    """
    if value is None:
        raise ValueError("Actual acquisition date cannot be None.")

    val_str = str(value).strip()
    if " " in val_str:
        val_str = val_str.split(" ")[0]
    elif "T" in val_str:
        val_str = val_str.split("T")[0]

    if hasattr(value, "date"):
        try:
            return value.date().isoformat()
        except Exception:
            pass

    return val_str


def _derive_actual_range(
    request: RawAcquisitionRequest,
    dataframe: object,
) -> tuple[str, str]:
    if dataframe is None or getattr(dataframe, "empty", True):
        raise ValueError("Cannot derive actual acquisition range from empty dataframe.")

    # 1. Check for a 'Date' or 'date' column first (supporting flat columns and MultiIndex tuples)
    columns = getattr(dataframe, "columns", None)
    if columns is not None:
        for col in columns:
            col_name = col[0] if isinstance(col, tuple) else col
            if str(col_name).strip().lower() == "date":
                col_series = dataframe[col]
                if not col_series.empty:
                    actual_start = _normalize_actual_date(col_series.min())
                    actual_end = _normalize_actual_date(col_series.max())
                    return actual_start, actual_end

    # 2. Fallback to index if it's a datetime/timestamp-capable index (not RangeIndex or numeric)
    index = getattr(dataframe, "index", None)
    if index is not None and not index.empty:
        if not isinstance(index, pd.RangeIndex) and not pd.api.types.is_numeric_dtype(index):
            actual_start = _normalize_actual_date(index.min())
            actual_end = _normalize_actual_date(index.max())
            return actual_start, actual_end

    # 3. Fail closed if actual coverage cannot be definitively derived
    raise ValueError(
        "Unable to derive actual acquisition date range "
        "from provider response."
    )


def execute_raw_acquisition(
    request: RawAcquisitionRequest,
    data_source: HistoricalDataSource | None = None,
) -> RawAcquisitionResult:
    source = (
        data_source
        if data_source is not None
        else YFinanceDataSource()
    )

    bars = source.fetch_daily(
        symbol=request.symbol,
        start_date=request.requested_start,
        end_date=request.requested_end,
    )

    raw_bytes = bars.raw_csv_bytes

    if raw_bytes is None:
        raise ValueError(
            "Provider adapter returned HistoricalBars without "
            "raw_csv_bytes."
        )

    if not isinstance(raw_bytes, bytes):
        raise TypeError(
            "HistoricalBars.raw_csv_bytes must contain bytes."
        )

    actual_start, actual_end = _derive_actual_range(
        request,
        bars.dataframe,
    )

    metadata = RawMetadata(
        provider=request.provider,
        provider_adapter_version=DEFAULT_PROVIDER_ADAPTER_VERSION,
        symbol=request.symbol,
        requested_start=request.requested_start,
        requested_end=request.requested_end,
        actual_start=actual_start,
        actual_end=actual_end,
        interval=request.interval,
        adjustment_mode=request.adjustment_policy,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        raw_format="csv",
    )

    provenance = RawProvenance(
        request_id=request.request_id,
        raw_bytes=raw_bytes,
    )

    return RawAcquisitionResult(
        request=request,
        metadata=metadata,
        provenance=provenance,
        raw_bytes=raw_bytes,
    )
