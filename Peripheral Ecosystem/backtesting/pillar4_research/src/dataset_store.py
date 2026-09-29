import os
import json
import hashlib
import pathlib
import pandas as pd
from typing import Tuple, Dict, Any, List, NamedTuple
from src.calendar_adapter import CalendarMetadata

class DatasetConflictError(Exception):
    """Raised when a dataset or manifest conflicts with an existing store entry."""
    pass

class DatasetIntegrityError(Exception):
    """Raised when a stored dataset, manifest, or identity hash fails verification."""
    pass

class StoreResult(NamedTuple):
    dataset_identity: str
    dataset_sha256: str
    is_new: bool

def canonicalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a canonically sorted and formatted DataFrame copy."""
    if df.empty:
        return df.copy()
    
    df_canon = df.copy()
    
    # Ensure timestamp is datetime UTC and sort by it
    if 'timestamp' in df_canon.columns:
        df_canon['timestamp'] = pd.to_datetime(df_canon['timestamp'], utc=True)
        df_canon = df_canon.sort_values('timestamp').reset_index(drop=True)
    
    # Canonicalize columns (alphabetical order)
    df_canon = df_canon[sorted(df_canon.columns)]
    
    # Normalize numeric columns to float representation
    for col in df_canon.columns:
        if col != 'timestamp' and pd.api.types.is_numeric_dtype(df_canon[col]):
            df_canon[col] = df_canon[col].astype(float)
            
    return df_canon

def compute_dataset_sha256(df: pd.DataFrame) -> str:
    """Compute a deterministic, canonical SHA256 hash for an OHLCV DataFrame."""
    if df.empty:
        return hashlib.sha256(b"empty").hexdigest()
    
    df_canon = canonicalize_dataframe(df)
    
    # Convert to CSV bytes without index for stable serialization
    csv_bytes = df_canon.to_csv(index=False, float_format="%.6f", lineterminator="\n").encode('utf-8')
    return hashlib.sha256(csv_bytes).hexdigest()

def compute_dataset_identity(df: pd.DataFrame, calendar_metadata: Any) -> str:
    """Compute combined dataset identity binding dataset_sha256 and calendar sha256."""
    d_sha = compute_dataset_sha256(df)
    c_sha = getattr(calendar_metadata, 'sha256', str(calendar_metadata))
    combined = f"{d_sha}:{c_sha}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

class DatasetStore:
    def __init__(self, root_dir: pathlib.Path):
        self.root_dir = pathlib.Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        (self.root_dir / "datasets").mkdir(exist_ok=True)
        (self.root_dir / "manifests").mkdir(exist_ok=True)
        (self.root_dir / "tmp").mkdir(exist_ok=True)

    def _get_paths(self, identity: str) -> Tuple[pathlib.Path, pathlib.Path]:
        ds_path = self.root_dir / "datasets" / f"{identity}.csv"
        mf_path = self.root_dir / "manifests" / f"{identity}.json"
        return ds_path, mf_path

    def store(self, df: pd.DataFrame, calendar_metadata: Any, symbol: str = "UNKNOWN", timeframe: str = "1d", strategy_id: str = None) -> StoreResult:
        if not hasattr(calendar_metadata, 'sha256'):
            raise TypeError("Invalid calendar metadata supplied; missing sha256.")

        df_canon = canonicalize_dataframe(df)
        d_sha = compute_dataset_sha256(df_canon)
        identity = compute_dataset_identity(df_canon, calendar_metadata)

        ds_path, mf_path = self._get_paths(identity)
        is_new = not (ds_path.exists() and mf_path.exists())

        if not is_new:
            # Verify integrity of existing
            existing_df, existing_meta = self.retrieve(identity)
            if existing_meta['dataset_sha256'] != d_sha:
                raise DatasetConflictError(f"Conflict: Identity {identity} already exists with different content.")
            return StoreResult(dataset_identity=identity, dataset_sha256=d_sha, is_new=False)

        # Write dataset and manifest atomically via tmp
        tmp_ds = self.root_dir / "tmp" / f"{identity}.csv"
        tmp_mf = self.root_dir / "tmp" / f"{identity}.json"

        csv_str = df_canon.to_csv(index=False, float_format="%.6f", lineterminator="\n")
        tmp_ds.write_text(csv_str, encoding="utf-8")
        
        manifest = {
            "dataset_identity": identity,
            "dataset_sha256": d_sha,
            "calendar_sha256": calendar_metadata.sha256,
            "symbol": symbol,
            "timeframe": timeframe,
            "strategy_id": strategy_id
        }
        tmp_mf.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        tmp_ds.replace(ds_path)
        tmp_mf.replace(mf_path)

        return StoreResult(dataset_identity=identity, dataset_sha256=d_sha, is_new=True)

    def retrieve(self, identity: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        ds_path, mf_path = self._get_paths(identity)
        
        if not ds_path.exists() or not mf_path.exists():
            raise DatasetIntegrityError(f"Missing dataset or manifest artifact for identity: {identity}")

        try:
            manifest = json.loads(mf_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise DatasetIntegrityError(f"Corrupted manifest for identity {identity}: {e}")

        if manifest.get('dataset_identity') != identity:
            raise DatasetIntegrityError(f"Manifest identity mismatch for {identity}")

        try:
            df = pd.read_csv(ds_path)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        except Exception as e:
            raise DatasetIntegrityError(f"Corrupted dataset CSV for identity {identity}: {e}")

        computed_d_sha = compute_dataset_sha256(df)

        if computed_d_sha != manifest.get('dataset_sha256'):
            raise DatasetIntegrityError("Dataset content hash does not match manifest record.")

        return df, manifest

    def get_manifest(self, identity: str) -> Dict[str, Any]:
        _, mf_path = self._get_paths(identity)
        if not mf_path.exists():
            raise DatasetIntegrityError(f"Manifest not found for {identity}")
        return json.loads(mf_path.read_text(encoding="utf-8"))

    # Tampering / Testing Helper Methods
    def store_with_forced_collision(self, df: pd.DataFrame, calendar_metadata: Any, symbol: str, timeframe: str):
        if not hasattr(calendar_metadata, 'sha256'):
            raise TypeError("Invalid calendar metadata supplied; missing sha256.")
        
        c_sha = calendar_metadata.sha256
        d_sha = compute_dataset_sha256(df)
        
        mf_dir = self.root_dir / "manifests"
        if mf_dir.exists():
            for p in mf_dir.glob("*.json"):
                try:
                    m = json.loads(p.read_text(encoding="utf-8"))
                    if (m.get("symbol") == symbol and 
                        m.get("timeframe") == timeframe and 
                        m.get("calendar_sha256") == c_sha and 
                        m.get("dataset_sha256") != d_sha):
                        raise DatasetConflictError("Conflict: Target already exists with a different dataset.")
                except DatasetConflictError:
                    raise
                except Exception:
                    continue

        return self.store(df, calendar_metadata, symbol=symbol, timeframe=timeframe)

    def tamper_manifest_collision(self, identity: str):
        _, mf_path = self._get_paths(identity)
        if mf_path.exists():
            data = json.loads(mf_path.read_text(encoding="utf-8"))
            data['dataset_sha256'] = 'f' * 64
            mf_path.write_text(json.dumps(data), encoding="utf-8")
        raise DatasetConflictError("Manifest collision simulated.")

    def tamper_dataset_content_file(self, identity: str):
        ds_path, _ = self._get_paths(identity)
        if ds_path.exists():
            ds_path.write_text("corrupted,csv,data,bytes\n", encoding="utf-8")

    def tamper_manifest_file(self, identity: str):
        _, mf_path = self._get_paths(identity)
        if mf_path.exists():
            mf_path.write_text("{invalid json content", encoding="utf-8")

    def inject_manifest_mismatch(self, identity: str):
        _, mf_path = self._get_paths(identity)
        if mf_path.exists():
            data = json.loads(mf_path.read_text(encoding="utf-8"))
            data['dataset_identity'] = 'wrong_identity_hash'
            mf_path.write_text(json.dumps(data), encoding="utf-8")

    def delete_manifest_file(self, identity: str):
        _, mf_path = self._get_paths(identity)
        if mf_path.exists():
            mf_path.unlink()

    def delete_dataset_file(self, identity: str):
        ds_path, _ = self._get_paths(identity)
        if ds_path.exists():
            ds_path.unlink()

    def create_orphan_tmp_artifact(self):
        tmp_file = self.root_dir / "tmp" / "orphan_test.tmp"
        tmp_file.write_text("orphan", encoding="utf-8")

    def list_valid_cache_entries(self) -> List[str]:
        valid = []
        mf_dir = self.root_dir / "manifests"
        if mf_dir.exists():
            for p in mf_dir.glob("*.json"):
                valid.append(p.stem)
        return valid
