from typing import Dict, Any, List
from trade_precheck_suite import TradePrecheckSuite
from governance_check_suite import GovernanceCheckSuite

class SOPExecutionAssistant:
    """
    Phase 7E Skill: SOP Execution Assistant
    Primary pre-flight trade coordinator. Executes an end-to-end pre-flight
    audit pipeline across Governance checks (7D) and Pre-Check Rules/Strategy (7C).
    """
    def __init__(self, name: str = "SOPExecutionAssistant"):
        self.name = name
        self.precheck_suite = TradePrecheckSuite()
        self.gov_suite = GovernanceCheckSuite()

    def execute(self, context: Any = None, **kwargs) -> Dict[str, Any]:
        data = {}
        if isinstance(context, dict):
            data.update(context)
        data.update(kwargs)

        ticker = data.get("ticker", "UNKNOWN")

        # Step 1: Governance & Circuit Breakers Audit (Phase 7D)
        gov_res = self.gov_suite.execute(data)
        gov_passed = gov_res.get("governance_cleared", False)

        # Step 2: Trade Precheck Audit (Phase 7C: Rules + Strategy)
        precheck_res = self.precheck_suite.execute(data)
        precheck_passed = precheck_res.get("overall_approved", False)

        # Step 3: Actionable Verdict Generation
        if gov_passed and precheck_passed:
            execution_decision = "EXECUTE"
            actionable_reason = "All governance checks, compliance rules, and technical setup parameters successfully validated."
        elif not gov_passed:
            execution_decision = "REJECTED_GOVERNANCE"
            actionable_reason = f"Blocked by Governance/Circuit Breaker: {', '.join(gov_res.get('violations', []))}"
        else:
            execution_decision = f"REJECTED_PRECHECK_{precheck_res.get('precheck_status', 'UNKNOWN')}"
            actionable_reason = "Trade proposal failed compliance rules or technical setup analysis pre-checks."

        return {
            "component": "SKILL",
            "skill_name": self.name,
            "ticker": ticker,
            "execution_decision": execution_decision,
            "is_approved": (execution_decision == "EXECUTE"),
            "actionable_reason": actionable_reason,
            "governance_audit": gov_res,
            "precheck_audit": precheck_res
        }
