from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Union

from historical_acquisition.contracts import (
    RawAcquisitionRequest,
    RawAcquisitionResult,
    RawMetadata,
    RawProvenance,
)
from historical_acquisition.acquisition_service import execute_raw_acquisition


class CacheIntegrityError(Exception):
    """Raised when an existing cache entry is missing, incomplete, tampered, or inconsistent."""
    pass


class CacheConflictError(Exception):
    """Raised when attempting to store a conflicting artifact for an already-existing request_id."""
    pass


class LocalHistoricalCache:
    """
    Immutable local historical raw data cache enforcing strict cryptographic and 
    provenance verification, fail-closed integrity governance, and atomic persistence.
    """

    def __init__(self, base_dir: Union[str, Path]) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, request: RawAcquisitionRequest) -> str:
        """Cache identity derived exclusively from canonical request identity (request_id)."""
        return request.request_id

    def _detect_misplaced_entry(self, request_id: str) -> None:
        """Detect an entry for request_id stored under a different directory name."""
        if not self.base_dir.exists():
            return

        for child in self.base_dir.iterdir():
            if not child.is_dir() or child.name == request_id:
                continue

            manifest_path = child / "manifest.json"
            if not manifest_path.is_file():
                continue

            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError, UnicodeError):
                continue

            if data.get("request_id") == request_id:
                raise CacheIntegrityError(
                    f"Cache directory identity mismatch: request {request_id} "
                    f"found in directory {child.name} instead of expected key directory."
                )

    def _get_entry_dir(self, request_id: str) -> Path:
        return self.base_dir / request_id

    def execute_and_build_result(self, request: RawAcquisitionRequest, data_source: Any) -> RawAcquisitionResult:
        """Executes raw acquisition via service boundary and returns RawAcquisitionResult."""
        return execute_raw_acquisition(request, data_source=data_source)

    def store(self, result: RawAcquisitionResult) -> None:
        """
        Atomically persists a RawAcquisitionResult into the immutable local cache.
        Raises CacheConflictError if an entry already exists with different bytes/hash.
        """
        request = result.request
        request_id = self.get_cache_key(request)
        entry_dir = self._get_entry_dir(request_id)
        raw_file = entry_dir / "raw_data.csv"
        manifest_file = entry_dir / "manifest.json"

        # Full validation of existing entry before deciding conflict vs idempotent accept
        if entry_dir.exists() and raw_file.exists() and manifest_file.exists():
            try:
                manifest_content = manifest_file.read_text(encoding="utf-8")
                manifest_data = json.loads(manifest_content)
                existing_bytes = raw_file.read_bytes()
                computed_sha = hashlib.sha256(existing_bytes).hexdigest()

                if manifest_data.get("request_id") != request_id or computed_sha != result.provenance.raw_sha256:
                    raise CacheConflictError(
                        f"Existing cache entry for {request_id} conflicts with new acquisition provenance or bytes."
                    )
                # Valid matching existing entry -> idempotent success
                return
            except CacheConflictError:
                raise
            except Exception as e:
                raise CacheConflictError(f"Error validating existing cache entry during store: {e}") from e

        # Atomic persistence via staging directory
        entry_dir.mkdir(parents=True, exist_ok=True)
        staging_dir = entry_dir / f".staging_{os.getpid()}_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        staging_dir.mkdir(parents=True, exist_ok=True)

        try:
            staged_raw = staging_dir / "raw_data.csv"
            staged_raw.write_bytes(result.raw_bytes)

            manifest_data = {
                "request_id": request_id,
                "provider": request.provider,
                "symbol": request.symbol,
                "requested_start": request.requested_start,
                "requested_end": request.requested_end,
                "interval": request.interval,
                "adjustment_policy": request.adjustment_policy,
                "acquisition_id": result.provenance.acquisition_id,
                "provider_adapter_version": result.metadata.provider_adapter_version,
                "actual_start": result.metadata.actual_start,
                "actual_end": result.metadata.actual_end,
                "retrieved_at": result.metadata.retrieved_at,
                "raw_format": result.metadata.raw_format,
                "raw_sha256": result.provenance.raw_sha256,
                "artifact_filename": "raw_data.csv",
            }

            staged_manifest = staging_dir / "manifest.json"
            staged_manifest.write_text(
                json.dumps(manifest_data, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
                encoding="utf-8"
            )

            if raw_file.exists() or manifest_file.exists():
                raise CacheConflictError(f"Concurrent write detected for cache entry {request_id}")

            staged_raw.replace(raw_file)
            staged_manifest.replace(manifest_file)

        finally:
            if staging_dir.exists():
                shutil.rmtree(staging_dir, ignore_errors=True)

    def get_or_execute(self, request: RawAcquisitionRequest, data_source: Any) -> RawAcquisitionResult:
        """
        Retrieves a valid cached RawAcquisitionResult if present and verified.
        Fails closed on any integrity or corruption error (NO automatic reacquisition).
        Executes acquisition on a true cache miss and persists atomically.
        """
        request_id = self.get_cache_key(request)
        entry_dir = self._get_entry_dir(request_id)
        raw_file = entry_dir / "raw_data.csv"
        manifest_file = entry_dir / "manifest.json"

        has_dir = entry_dir.exists()
        has_raw = raw_file.exists()
        has_manifest = manifest_file.exists()

        # STATE 1: CACHE MISS
        if not has_dir and not has_raw and not has_manifest:
            self._detect_misplaced_entry(request_id)
            result = self.execute_and_build_result(request, data_source=data_source)
            self.store(result)
            return result

        # STATE 2: INTEGRITY FAILURE (Incomplete entry)
        if not (has_dir and has_raw and has_manifest):
            raise CacheIntegrityError(
                f"Incomplete cache entry for {request_id}: missing required files (dir={has_dir}, raw={has_raw}, manifest={has_manifest})."
            )

        try:
            manifest_content = manifest_file.read_text(encoding="utf-8")
            manifest_data = json.loads(manifest_content)
        except Exception as e:
            raise CacheIntegrityError(f"Malformed manifest JSON for {request_id}: {e}") from e

        if manifest_data.get("request_id") != request_id:
            raise CacheIntegrityError(
                f"Manifest request_id mismatch: expected {request_id}, found {manifest_data.get('request_id')}."
            )

        try:
            reconstructed_request = RawAcquisitionRequest(
                provider=manifest_data["provider"],
                symbol=manifest_data["symbol"],
                requested_start=manifest_data["requested_start"],
                requested_end=manifest_data["requested_end"],
                interval=manifest_data["interval"],
                adjustment_policy=manifest_data["adjustment_policy"],
            )
            if reconstructed_request.request_id != request_id:
                raise CacheIntegrityError("Manifest canonical request fields do not reconstruct cache key.")
        except Exception as e:
            raise CacheIntegrityError(f"Invalid request fields in manifest for {request_id}: {e}") from e

        try:
            raw_bytes = raw_file.read_bytes()
        except Exception as e:
            raise CacheIntegrityError(f"Failed to read raw artifact for {request_id}: {e}") from e

        computed_sha = hashlib.sha256(raw_bytes).hexdigest()
        manifest_sha = manifest_data.get("raw_sha256")
        if computed_sha != manifest_sha:
            raise CacheIntegrityError(
                f"Artifact SHA-256 mismatch for {request_id}: computed {computed_sha}, manifest recorded {manifest_sha}."
            )

        try:
            metadata = RawMetadata(
                provider=manifest_data["provider"],
                provider_adapter_version=manifest_data["provider_adapter_version"],
                symbol=manifest_data["symbol"],
                requested_start=manifest_data["requested_start"],
                requested_end=manifest_data["requested_end"],
                interval=manifest_data["interval"],
                adjustment_mode=manifest_data["adjustment_policy"],
                actual_start=manifest_data["actual_start"],
                actual_end=manifest_data["actual_end"],
                retrieved_at=manifest_data["retrieved_at"],
                raw_format=manifest_data["raw_format"],
            )

            provenance = RawProvenance(
                request_id=request_id,
                raw_bytes=raw_bytes,
                acquisition_id=manifest_data["acquisition_id"],
            )
        except (ValueError, KeyError, TypeError) as e:
            raise CacheIntegrityError(
                f"Invalid cache metadata or provenance for {request_id}: {e}"
            ) from e

        return RawAcquisitionResult(
            request=reconstructed_request,
            metadata=metadata,
            provenance=provenance,
            raw_bytes=raw_bytes,
        )

