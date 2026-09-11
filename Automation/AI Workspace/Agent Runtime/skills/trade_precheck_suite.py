from typing import Dict, Any, List
from rule_verification_suite import RuleVerificationSuite
from strategy_analysis_suite import StrategyAnalysisSuite

class TradePrecheckSuite:
    """
    Phase 7C Skill: Integrated Trade Pre-Check Suite
    Combines Phase 7A (Rule Verification) and Phase 7B (Strategy Analysis)
    into a single pre-flight trade audit.
    """
    def __init__(self, name: str = "TradePrecheckSuite"):
        self.name = name
        self.rule_suite = RuleVerificationSuite()
        self.strategy_suite = StrategyAnalysisSuite()

    def execute(self, context: Any = None, **kwargs) -> Dict[str, Any]:
        data = {}
        if isinstance(context, dict):
            data.update(context)
        data.update(kwargs)

        ticker = data.get("ticker", "UNKNOWN")

        # Step 1: Execute Rule Verification
        rule_res = self.rule_suite.execute(data)

        # Step 2: Execute Strategy Analysis
        strat_res = self.strategy_suite.execute(data)

        # Step 3: Integrate Evaluation
        rule_pass = rule_res.get("compliant", False)
        strat_pass = strat_res.get("valid_setup", False)

        overall_approved = rule_pass and strat_pass

        if rule_pass and strat_pass:
            precheck_status = "APPROVED"
        elif not rule_pass and not strat_pass:
            precheck_status = "REJECTED_MULTIPLE"
        elif not rule_pass:
            precheck_status = "REJECTED_RULES"
        else:
            precheck_status = "REJECTED_STRATEGY"

        return {
            "component": "SKILL",
            "skill_name": self.name,
            "ticker": ticker,
            "overall_approved": overall_approved,
            "precheck_status": precheck_status,
            "rule_verification": {
                "compliant": rule_pass,
                "violations": rule_res.get("violations", []),
                "passed_rules": rule_res.get("passed_rules", [])
            },
            "strategy_analysis": {
                "valid_setup": strat_pass,
                "failed_checks": strat_res.get("failed_checks", []),
                "passed_checks": strat_res.get("passed_checks", [])
            }
        }
