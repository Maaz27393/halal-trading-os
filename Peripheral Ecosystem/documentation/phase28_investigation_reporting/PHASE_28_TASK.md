# Phase 28 — Automated Investigation & Incident Reporting Master Specification

## Objective
Establish an automated investigation and incident reporting engine that consumes Phase 27 multi-domain evidence, performs rigorous structured analysis (separating observed facts, derived findings, and unresolved questions), and generates immutable canonical JSON and human-readable reports under strict read-only guarantees.

## Core Tracks & Blueprints
- **28A_INVESTIGATION_INTAKE.md** — Standardized request intake and unique tracking ID generation.
- **28B_EVIDENCE_COLLECTION.md** — Multi-domain evidence aggregation preserving source provenance.
- **28C_INVESTIGATION_ANALYSIS.md** — Analytical engine separating facts, derived insights, and unresolved items.
- **28D_REPORT_GENERATION.md** — Canonical JSON and Markdown/HTML report serialization.
- **28E_SAFETY_GOVERNANCE.md** — Enforcement of zero execution authority and read-only invariants.
- **28F_VALIDATION.md** — End-to-end testing protocol verifying evidence fidelity and report determinism.

## Critical Boundaries
- **Strictly Observational:** Reports anomalies and evidence only; zero automated remediation, provider alteration, or trading execution.
