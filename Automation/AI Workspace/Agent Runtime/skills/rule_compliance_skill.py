from typing import Dict, Any

class VerifyRuleComplianceSkill:
    """
    Skill to verify if a trade proposal complies with L0/L1 trading rules.
    """
    def __init__(self, name: str = "VerifyRuleComplianceSkill", max_risk_pct: float = 1.0, max_positions_day: int = 3):
        self.name = name
        self.max_risk_pct = max_risk_pct
        self.max_positions_day = max_positions_day

    def execute(self, context: Any = None, **kwargs) -> Dict[str, Any]:
        data = {}
        if isinstance(context, dict):
            data.update(context)
        data.update(kwargs)

        proposed_risk = float(data.get("proposed_risk_pct", 0.5))
        positions_today = int(data.get("positions_today", 0))
        is_cash_trade = bool(data.get("is_cash_trade", True))

        violations = []
        if proposed_risk > self.max_risk_pct:
            violations.append(f"Proposed risk {proposed_risk}% exceeds max allowed {self.max_risk_pct}%.")
        if positions_today >= self.max_positions_day:
            violations.append(f"Positions today ({positions_today}) meets or exceeds daily limit ({self.max_positions_day}).")
        if not is_cash_trade:
            violations.append("Non-cash/leveraged trade violates Halal cash-only mandate.")

        compliant = len(violations) == 0
        return {
            "component": "SKILL",
            "skill_name": self.name,
            "compliant": compliant,
            "violations": violations,
            "metrics_checked": {
                "proposed_risk_pct": proposed_risk,
                "positions_today": positions_today,
                "is_cash_trade": is_cash_trade
            }
        }
