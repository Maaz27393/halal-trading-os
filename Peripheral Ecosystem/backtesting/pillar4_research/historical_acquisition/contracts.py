from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime


SUPPORTED_PROVIDERS = frozenset({"yfinance"})
SUPPORTED_INTERVALS = frozenset({"1d"})
SUPPORTED_ADJUSTMENT_POLICIES = frozenset({"RAW_UNADJUSTED"})

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _normalize_date(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")

    value = value.strip()

    if not _DATE_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} must use YYYY-MM-DD format."
        )

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be a valid calendar date."
        ) from exc

    return value


def _canonical_request_payload(
    *,
    provider: str,
    symbol: str,
    requested_start: str,
    requested_end: str,
    interval: str,
    adjustment_policy: str,
) -> dict[str, str]:
    return {
        "provider": provider,
        "symbol": symbol,
        "requested_start": requested_start,
        "requested_end": requested_end,
        "interval": interval,
        "adjustment_policy": adjustment_policy,
    }


def _compute_request_id(payload: dict[str, str]) -> str:
    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class RawAcquisitionRequest:
    """
    Immutable request contract for B.4 raw historical-data acquisition.

    request_id is deterministic for the canonical request identity.
    """

    provider: str
    symbol: str
    requested_start: str
    requested_end: str
    interval: str
    adjustment_policy: str
    request_id: str = field(init=False)

    def __post_init__(self) -> None:
        provider = str(self.provider).lower().strip()
        symbol = str(self.symbol).upper().strip()
        requested_start = _normalize_date(
            self.requested_start,
            "requested_start",
        )
        requested_end = _normalize_date(
            self.requested_end,
            "requested_end",
        )
        interval = str(self.interval).lower().strip()
        adjustment_policy = (
            str(self.adjustment_policy).upper().strip()
        )

        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider '{provider}'. "
                f"Supported providers: {sorted(SUPPORTED_PROVIDERS)}."
            )

        if not symbol:
            raise ValueError("symbol must not be empty.")

        if not re.fullmatch(r"[A-Z0-9._-]+", symbol):
            raise ValueError(
                "symbol contains unsupported characters."
            )

        if requested_start > requested_end:
            raise ValueError(
                "requested_start must not be later than requested_end."
            )

        if interval not in SUPPORTED_INTERVALS:
            raise ValueError(
                f"Unsupported interval '{interval}'. "
                f"Supported intervals: {sorted(SUPPORTED_INTERVALS)}."
            )

        if adjustment_policy not in SUPPORTED_ADJUSTMENT_POLICIES:
            raise ValueError(
                f"Unsupported adjustment policy "
                f"'{adjustment_policy}'. "
                f"Supported policies: "
                f"{sorted(SUPPORTED_ADJUSTMENT_POLICIES)}."
            )

        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "requested_start", requested_start)
        object.__setattr__(self, "requested_end", requested_end)
        object.__setattr__(self, "interval", interval)
        object.__setattr__(
            self,
            "adjustment_policy",
            adjustment_policy,
        )

        request_payload = _canonical_request_payload(
            provider=provider,
            symbol=symbol,
            requested_start=requested_start,
            requested_end=requested_end,
            interval=interval,
            adjustment_policy=adjustment_policy,
        )

        object.__setattr__(
            self,
            "request_id",
            _compute_request_id(request_payload),
        )


@dataclass(frozen=True)
class RawMetadata:
    """
    Metadata describing the actual provider-returned raw artifact.

    B.4 records actual coverage but does not determine calendar
    completeness. Completeness remains a downstream qualification concern.
    """

    provider: str
    provider_adapter_version: str
    symbol: str
    requested_start: str
    requested_end: str
    actual_start: str
    actual_end: str
    interval: str
    adjustment_mode: str
    retrieved_at: str
    raw_format: str = "csv"

    def __post_init__(self) -> None:
        provider = str(self.provider).lower().strip()
        symbol = str(self.symbol).upper().strip()
        requested_start = _normalize_date(
            self.requested_start,
            "requested_start",
        )
        requested_end = _normalize_date(
            self.requested_end,
            "requested_end",
        )
        actual_start = _normalize_date(
            self.actual_start,
            "actual_start",
        )
        actual_end = _normalize_date(
            self.actual_end,
            "actual_end",
        )
        interval = str(self.interval).lower().strip()
        adjustment_mode = str(self.adjustment_mode).upper().strip()
        adapter_version = str(
            self.provider_adapter_version
        ).strip()
        retrieved_at = str(self.retrieved_at).strip()
        raw_format = str(self.raw_format).lower().strip()

        if not provider:
            raise ValueError("provider must not be empty.")

        if not symbol:
            raise ValueError("symbol must not be empty.")

        if not adapter_version:
            raise ValueError(
                "provider_adapter_version must not be empty."
            )

        if not retrieved_at:
            raise ValueError(
                "retrieved_at must not be empty."
            )

        if not raw_format:
            raise ValueError("raw_format must not be empty.")

        if actual_start > actual_end:
            raise ValueError(
                "actual_start must not be later than actual_end."
            )

        if interval not in SUPPORTED_INTERVALS:
            raise ValueError(
                f"Unsupported interval '{interval}'."
            )

        if adjustment_mode not in SUPPORTED_ADJUSTMENT_POLICIES:
            raise ValueError(
                f"Unsupported adjustment mode "
                f"'{adjustment_mode}'."
            )

        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(
            self,
            "requested_start",
            requested_start,
        )
        object.__setattr__(
            self,
            "requested_end",
            requested_end,
        )
        object.__setattr__(
            self,
            "actual_start",
            actual_start,
        )
        object.__setattr__(
            self,
            "actual_end",
            actual_end,
        )
        object.__setattr__(self, "interval", interval)
        object.__setattr__(
            self,
            "adjustment_mode",
            adjustment_mode,
        )
        object.__setattr__(
            self,
            "provider_adapter_version",
            adapter_version,
        )
        object.__setattr__(
            self,
            "retrieved_at",
            retrieved_at,
        )
        object.__setattr__(
            self,
            "raw_format",
            raw_format,
        )


@dataclass(frozen=True)
class RawProvenance:
    """
    Identity of one concrete raw acquisition event.

    raw_bytes are authoritative. raw_sha256 is derived exclusively
    from those exact bytes and therefore cannot be independently
    supplied by a caller.
    """

    request_id: str
    raw_bytes: bytes
    acquisition_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    raw_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        request_id = str(self.request_id).strip()
        acquisition_id = str(self.acquisition_id).strip()

        if not request_id:
            raise ValueError(
                "request_id must not be empty."
            )

        if not acquisition_id:
            raise ValueError(
                "acquisition_id must not be empty."
            )

        if not isinstance(self.raw_bytes, bytes):
            raise TypeError(
                "raw_bytes must contain bytes."
            )

        raw_sha256 = hashlib.sha256(
            self.raw_bytes
        ).hexdigest()

        object.__setattr__(
            self,
            "request_id",
            request_id,
        )
        object.__setattr__(
            self,
            "acquisition_id",
            acquisition_id,
        )
        object.__setattr__(
            self,
            "raw_sha256",
            raw_sha256,
        )


@dataclass(frozen=True)
class RawAcquisitionResult:
    """
    Complete B.4 raw acquisition boundary.

    raw_bytes are the exact adapter-produced CSV bytes.
    """

    request: RawAcquisitionRequest
    metadata: RawMetadata
    provenance: RawProvenance
    raw_bytes: bytes

    def __post_init__(self) -> None:
        if not isinstance(
            self.request,
            RawAcquisitionRequest,
        ):
            raise TypeError(
                "request must be RawAcquisitionRequest."
            )

        if not isinstance(
            self.metadata,
            RawMetadata,
        ):
            raise TypeError(
                "metadata must be RawMetadata."
            )

        if not isinstance(
            self.provenance,
            RawProvenance,
        ):
            raise TypeError(
                "provenance must be RawProvenance."
            )

        if not isinstance(self.raw_bytes, bytes):
            raise TypeError(
                "raw_bytes must contain bytes."
            )

        if self.provenance.request_id != self.request.request_id:
            raise ValueError(
                "provenance.request_id must match "
                "request.request_id."
            )

        if self.provenance.raw_bytes != self.raw_bytes:
            raise ValueError(
                "provenance.raw_bytes must match the exact "
                "raw_bytes carried by the result."
            )

        calculated_hash = hashlib.sha256(
            self.raw_bytes
        ).hexdigest()

        if self.provenance.raw_sha256 != calculated_hash:
            raise ValueError(
                "provenance.raw_sha256 does not match "
                "the exact raw_bytes."
            )

