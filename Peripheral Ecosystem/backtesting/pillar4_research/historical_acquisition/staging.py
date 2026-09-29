from __future__ import annotations

from pathlib import Path

from .source import HistoricalBars


def stage_raw_bars(
    bars: HistoricalBars,
    staging_dir: str | Path,
) -> Path:
    """
    Persist the provider's exact raw CSV bytes without transformation.

    This boundary intentionally does not:
    - reconstruct CSV from the DataFrame,
    - normalize OHLCV data,
    - calculate hashes,
    - perform calendar validation,
    - generate qualification manifests,
    - invoke P4.3 preparation.

    Those responsibilities belong to their respective downstream
    qualification and P4.3 boundaries.
    """
    if not isinstance(bars, HistoricalBars):
        raise TypeError(
            "bars must be an instance of HistoricalBars."
        )

    if bars.raw_csv_bytes is None:
        raise ValueError(
            "HistoricalBars.raw_csv_bytes is required for raw staging."
        )

    if not isinstance(bars.raw_csv_bytes, bytes):
        raise TypeError(
            "HistoricalBars.raw_csv_bytes must contain bytes."
        )

    staging_path = Path(staging_dir)
    staging_path.mkdir(parents=True, exist_ok=True)

    filename = f"{bars.symbol}_{bars.timeframe}_{bars.start_date}_{bars.end_date}.csv"
    output_path = staging_path / filename

    output_path.write_bytes(bars.raw_csv_bytes)

    return output_path
