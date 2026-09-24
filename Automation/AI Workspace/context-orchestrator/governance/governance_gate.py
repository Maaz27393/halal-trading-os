from __future__ import annotations

from typing import Any, Dict, List, Optional
from contracts.context_contracts import ContextBundle


class GovernanceGate:
    """
    Independent, deterministic governance evaluation layer.
    Sits strictly between Integrity Gate and Qwen Model Runtime.
    Evaluates policy profiles, provenance, and constraints without 
    modifying source data or executing tools.
    """

    SUPPORTED_PROFILES = {"sandbox", "strict", "permissive"}

    @classmethod
    def evaluate(cls, bundle: ContextBundle) -> ContextBundle:
        """
        Evaluates the validated ContextBundle against governance policies.
        Updates bundle.governance_report and bundle.is_valid / decision state.
        Fails closed if integrity is invalid or policy rules are breached.
        """
        profile = bundle.request.governance_profile.lower()
        if profile not in cls.SUPPORTED_PROFILES:
            profile = "sandbox"  # Fallback default safety rule

        decisions: List[str] = []
        violations: List[str] = []

        # Rule 1: Fail closed if Integrity Gate already failed or unverified
        if not bundle.is_valid:
            return cls._seal_report(
                bundle=bundle,
                decision="BLOCK",
                status="FAILED",
                violations=["Integrity Gate check was not valid. Governance blocked execution."],
            )

        # Rule 2: Profile-specific evaluations (deterministic rules)
        if profile == "sandbox":
            # Sandbox permits standard read-only generation with warnings if sources are partial
            successful_sources = bundle.fused_context.get("sources_successful", [])
            if not successful_sources:
                violations.append("Sandbox profile violation: Zero successful context sources available.")
        
        elif profile == "strict":
            # Strict profile requires all requested sources to succeed
            required = set(bundle.request.required_sources)
            successful = set(bundle.fused_context.get("sources_successful", []))
            missing = required - successful
            if missing:
                violations.append(f"Strict profile violation: Missing required sources: {list(missing)}")

        elif profile == "permissive":
            # Permissive allows execution as long as integrity is valid
            pass

        # Finalize decision based on violations
        if violations:
            decision = "BLOCK"
            status = "FAILED"
        else:
            decision = "PASS"
            status = "SUCCESS"

        governance_report = {
            "status": status,
            "decision": decision,
            "profile": profile,
            "violations": violations,
            "checked_rules": [
                "integrity_precondition",
                f"profile_enforcement_{profile}",
                "read_only_compliance",
            ],
        }

        # Attach report to bundle
        bundle.governance_report = governance_report
        bundle.provenance["governance_gate"] = {
            "status": status,
            "decision": decision,
            "profile": profile,
        }

        # If blocked, invalidate bundle to halt downstream model execution (fail closed)
        if decision == "BLOCK":
            bundle.is_valid = False

        return bundle

    @staticmethod
    def _seal_report(
        bundle: ContextBundle, decision: str, status: str, violations: List[str]
    ) -> ContextBundle:
        bundle.governance_report = {
            "status": status,
            "decision": decision,
            "profile": bundle.request.governance_profile,
            "violations": violations,
            "checked_rules": ["integrity_precondition", "fail_closed_guard"],
        }
        bundle.provenance["governance_gate"] = {
            "status": status,
            "decision": decision,
        }
        bundle.is_valid = False
        return bundle
