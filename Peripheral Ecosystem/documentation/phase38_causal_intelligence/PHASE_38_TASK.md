# Phase 38 — Causal Analysis & Root-Cause Intelligence Master Specification

## Objective
Establish a read-only causal analysis layer that constructs evidence chains from telemetry, evaluates candidate root causes while distinguishing correlation from causation, maintains dependency and influence graphs with provenance, and packages root-cause intelligence for human review under Phase 18 change governance.

## Core Tracks & Blueprints
- **38A_CAUSAL_EVIDENCE_MODELING.md** — Construction of explicit evidence chains (`OBSERVED`, `TEMPORAL_ASSOCIATION`, `CORRELATED`, `CANDIDATE_CAUSE`, `UNCONFIRMED`).
- **38B_ROOT_CAUSE_DETECTION.md** — Cross-domain relationship analysis across providers, latency, errors, capacity, and risk.
- **38C_DEPENDENCY_INFLUENCE_GRAPH.md** — Machine-readable relationship graphs with traceable provenance for every edge.
- **38D_ROOT_CAUSE_CONFIDENCE.md** — Confidence scoring, contradictory evidence tracking, and uncertainty evaluation.
- **38E_KNOWLEDGE_INVESTIGATION_INTEGRATION.md** — Bridge adapters converting root causes into Phase 27 KnowledgeObjects for Phase 28 investigations.
- **38F_VALIDATION.md** — Test protocols verifying causal analysis correctness and read-only invariants.

## Critical Boundaries
- **Analysis Only & Read-Only:** Zero automated remediation, zero auto-scaling, zero automated decisions, zero execution authority.
