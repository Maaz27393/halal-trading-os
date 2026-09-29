from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from src.calendar_adapter import CalendarMetadata
from src.dataset_store import DatasetStore, DatasetIntegrityError
from src.backtest_dataset import BacktestDataset, DatasetMutationError

class DatasetLoaderError(Exception):
    """Raised when backtest dataset loading fails due to boundary or integrity violations."""
    pass

def load_backtest_dataset(
    store: DatasetStore,
    dataset_identity: str,
    calendar_metadata: CalendarMetadata
) -> BacktestDataset:
    # R08: Raw unverified calendar rejected (must be a CalendarMetadata instance)
    if not isinstance(calendar_metadata, CalendarMetadata):
        raise TypeError("Calendar must be a verified CalendarMetadata instance.")

    # R02 - R06: Load and verify dataset integrity via P4.3 DatasetStore.retrieve()
    try:
        df, manifest = store.retrieve(dataset_identity)
    except Exception as e:
        raise DatasetLoaderError(f"Dataset integrity or existence failure: {e}") from e

    # R07: Verify calendar metadata matches the dataset's bound calendar provenance
    if manifest.get("calendar_sha256") != calendar_metadata.sha256:
        raise DatasetLoaderError("Calendar provenance mismatch: calendar SHA256 does not match dataset binding.")

    dataset_sha256 = manifest.get("dataset_sha256", dataset_identity)
    calendar_sha256 = manifest.get("calendar_sha256", calendar_metadata.sha256)

    return BacktestDataset(
        dataset_identity=dataset_identity,
        dataset_sha256=dataset_sha256,
        calendar_sha256=calendar_sha256,
        df=df,
        calendar_metadata=calendar_metadata
    )
