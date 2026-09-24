from __future__ import annotations

from typing import Any, Dict, List

from contracts.context_contracts import ContextBundle


class IntegrityGate:
    """
    Deterministic read-only integrity validator.
    Ensures that required sources succeeded and the context bundle is structurally sound
    before downstream consumption.
    """

    @staticmethod
    def validate(bundle: ContextBundle) -> ContextBundle:
        checks: List[Dict[str, Any]] = []
        errors: List[str] = []

        # Check 1: Required sources verification
        required = set(bundle.request.required_sources)
        successful_providers = {p.provider for p in bundle.successful_results()}

        missing_required = required - successful_providers
        if missing_required:
            checks.append({
                "check": "required_sources_present",
                "status": "FAIL",
                "missing": list(missing_required),
            })
            errors.append(f"Required sources failed or unavailable: {list(missing_required)}")
        else:
            checks.append({
                "check": "required_sources_present",
                "status": "PASS",
            })

        # Check 2: At least one provider succeeded if no hard requirement
        if not bundle.successful_results() and (bundle.request.required_sources or bundle.request.optional_sources):
            checks.append({
                "check": "any_successful_provider",
                "status": "FAIL",
            })
            errors.append("All queried context providers failed or returned unavailable status.")
        else:
            checks.append({
                "check": "any_successful_provider",
                "status": "PASS",
            })

        overall_status = "VALID" if not errors else "INVALID"

        bundle.integrity_report = {
            "status": overall_status,
            "checks": checks,
            "errors": errors,
        }

        return bundle
