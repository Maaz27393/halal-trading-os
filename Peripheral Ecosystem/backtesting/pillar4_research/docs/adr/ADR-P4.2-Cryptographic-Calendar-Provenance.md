# ADR-P4.2: Cryptographic Calendar Provenance and Validation Gate Integration

* **Status:** APPROVED & FROZEN
* **Pillar:** Pillar 4 — Backtesting & Research Infrastructure
* **Phase:** P4.2
* **Decision Type:** Architecture / Data Integrity / Reproducibility

## Context
Historical backtesting depends on deterministic knowledge of which market sessions were valid trading sessions. An unverified, mutable, or externally changing trading calendar can introduce:
* incorrect session inclusion or exclusion;
* missing-bar discrepancies;
* calendar drift between runs;
* reproducibility failures;
* ambiguous dataset provenance; and
* potential historical validation errors.

The trading calendar therefore needs to be treated as an immutable, versioned research artifact rather than a live dependency.

## Decision

### 1. Cryptographic Calendar Identity
Every calendar artifact must contain a canonical SHA-256 fingerprint. The hash is computed from the canonicalized calendar payload while excluding the fingerprint field itself. Key sorting and deterministic serialization ensure that equivalent payloads produce the same fingerprint. Both sha256 and calendar_sha256 fingerprint fields are excluded from the canonical hash input to prevent recursive self-reference.

### 2. Dedicated Calendar Verification Boundary
A dedicated calendar_adapter.py module is responsible for:
* loading the calendar artifact;
* validating its structural schema;
* validating required metadata;
* validating session structures;
* canonicalizing the payload;
* computing the expected SHA-256 fingerprint;
* comparing the computed fingerprint with the stored fingerprint; and
* returning verified CalendarMetadata.

Invalid, malformed, incomplete, or tampered artifacts fail closed.

### 3. Verification Before Validation
Calendar verification must occur before calendar data enters the OHLCV validation pipeline. The architectural flow is:
Calendar File → Calendar Adapter → Verified CalendarMetadata → Integration Boundary → OHLCV Validator

The existing alidate_ohlcv() function remains responsible for deterministic OHLCV/data validation and does not perform calendar cryptographic verification.

### 4. Validator Decoupling
alidate_ohlcv() retains its existing calendar interface based on normalized Iterable[pd.Timestamp]. This preserves backward compatibility and keeps cryptographic concerns outside the foundational data validator.

### 5. Manifest Provenance Binding
Backtesting validation manifests must bind the dataset to the verified calendar identity. The manifest records:
* calendar_id
* calendar_version
* calendar_sha256

These values originate from verified CalendarMetadata, rather than arbitrary caller-supplied identity strings. The resulting provenance chain is:
Run ID → Dataset Version + Calendar Version + Strategy Version

### 6. Immutable Calendar Artifacts
Calendars are treated as immutable, versioned local research artifacts. A changed calendar requires a new calendar version/fingerprint rather than silently modifying an existing artifact.

## Security and Integrity Properties
The P4.2 implementation establishes the following guarantees:
* Calendar tampering is detected through SHA-256 verification.
* Missing fingerprints fail closed.
* Required metadata omissions fail closed.
* Malformed session entries fail closed.
* Unverified calendar metadata cannot legitimately enter the validation boundary.
* Manifest provenance is derived from verified calendar metadata.
* Calendar identity is deterministic and independently auditable.

## Verification
P4.2 verification completed with:
* 11/11 P4.2 tests passing
* Existing 8/8 foundational validator tests preserved
* Calendar canonicalization verified
* Fingerprint exclusion verified
* Tamper rejection verified
* Schema validation verified
* Validator integration verified
* Manifest provenance linkage verified

## Architectural Consequences

### Positive
* Deterministic historical-session handling
* Reproducible backtesting runs
* Explicit calendar provenance
* Cryptographically auditable research artifacts
* Separation of cryptographic integrity from data validation
* No dependency on live calendar APIs during historical validation

### Constraints
* Calendar artifacts must be versioned rather than modified in place.
* Dataset and calendar identities must remain independently tracked.
* Future backtesting components must consume verified calendar metadata rather than bypassing the adapter.

## Non-Goals
P4.2 does not implement:
* automated historical OHLCV acquisition;
* multi-asset dataset ingestion;
* market-data caching;
* backtest strategy execution;
* performance analytics;
* optimization;
* live trading;
* automatic order execution.
