import json
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

@dataclass
class QualificationManifest:
    source_identity: str
    provider: str
    symbol: str
    timeframe: str
    requested_start: str
    requested_end: str
    actual_first_date: str
    actual_last_date: str
    row_count: int
    retrieved_at: str
    adjustment_status: str
    calendar_identity: str
    calendar_sha256: str
    raw_sha256: str

    def to_dict(self) -> dict:
        return asdict(self)

class QualificationManager:
    @staticmethod
    def generate_manifest(
        csv_path: Path,
        source_identity: str,
        provider: str,
        symbol: str,
        timeframe: str,
        requested_start: str,
        requested_end: str,
        adjustment_status: str,
        calendar_identity: str,
        calendar_sha256: str
    ) -> QualificationManifest:
        raw_bytes = Path(csv_path).read_bytes()
        raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        
        # Derive row count strictly from persisted raw CSV bytes (excluding header)
        lines = [line for line in raw_bytes.splitlines() if line.strip()]
        row_count = max(0, len(lines) - 1) if lines else 0
        
        # Estimate date bounds from lines if present, fallback to requested range
        actual_first_date = requested_start
        actual_last_date = requested_end
        if row_count > 0 and len(lines) > 1:
            try:
                first_row_cols = lines[1].decode("utf-8").split(",")
                last_row_cols = lines[-1].decode("utf-8").split(",")
                actual_first_date = first_row_cols[0].strip()
                actual_last_date = last_row_cols[0].strip()
            except Exception:
                pass
        
        retrieved_at = datetime.now(timezone.utc).isoformat()
        
        return QualificationManifest(
            source_identity=source_identity,
            provider=provider,
            symbol=symbol,
            timeframe=timeframe,
            requested_start=requested_start,
            requested_end=requested_end,
            actual_first_date=actual_first_date,
            actual_last_date=actual_last_date,
            row_count=row_count,
            retrieved_at=retrieved_at,
            adjustment_status=adjustment_status,
            calendar_identity=calendar_identity,
            calendar_sha256=calendar_sha256,
            raw_sha256=raw_sha256
        )

    @staticmethod
    def verify_sidecar(csv_path: Path, manifest_path: Path) -> tuple[bool, str]:
        if not Path(csv_path).exists() or not Path(manifest_path).exists():
            return False, "Missing CSV or manifest file."
            
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            raw_bytes = Path(csv_path).read_bytes()
            current_hash = hashlib.sha256(raw_bytes).hexdigest()
            
            if current_hash != data.get("raw_sha256"):
                return False, f"Hash mismatch: expected {data.get('raw_sha256')}, got {current_hash}."
                
            return True, "OK"
        except Exception as e:
            return False, str(e)
