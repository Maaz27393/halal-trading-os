from typing import Dict, Any, List

class RuleVerificationSuite:
    """
    Phase 7A Skill: Rule Verification Suite
    Performs comprehensive deterministic checks on trade proposals against L0/L1 rules:
    - Max Risk per Trade (<= 1.0%)
    - Daily New Positions Cap (<= 2)
    - Cash-Only / Non-Leverage Mandate
    - Shariah Screening Compliance
    - Max Position Allocation (<= 20% total portfolio)
    """
    def __init__(self, name: str = "RuleVerificationSuite"):
        self.name = name
        self.max_risk_pct = 1.0
        self.max_daily_positions = 2
        self.max_position_size_pct = 20.0

    def execute(self, context: Any = None, **kwargs) -> Dict[str, Any]:
        data = {}
        if isinstance(context, dict):
            data.update(context)
        data.update(kwargs)

        ticker = data.get("ticker", "UNKNOWN")
        proposed_risk = float(data.get("proposed_risk_pct", 0.0))
        positions_today = int(data.get("positions_today", 0))
        is_cash_trade = bool(data.get("is_cash_trade", True))
        is_shariah_compliant = bool(data.get("is_shariah_compliant", True))
        position_size_pct = float(data.get("position_size_pct", 10.0))

        violations: List[str] = []
        passed_rules: List[str] = []

        # 1. Risk Check
        if proposed_risk > self.max_risk_pct:
            violations.append(f"Risk Violation: {proposed_risk}% exceeds max limit of {self.max_risk_pct}%.")
        else:
            passed_rules.append(f"Risk Check: {proposed_risk}% <= {self.max_risk_pct}% limit.")

        # 2. Daily Position Cap
        if positions_today >= self.max_daily_positions:
            violations.append(f"Frequency Violation: Positions today ({positions_today}) meets or exceeds daily limit ({self.max_daily_positions}).")
        else:
            passed_rules.append(f"Daily Frequency Check: {positions_today}/{self.max_daily_positions} positions taken.")

        # 3. Cash-Only Mandate
        if not is_cash_trade:
            violations.append("Structure Violation: Non-cash / leveraged / short trade violates Halal cash-only mandate.")
        else:
            passed_rules.append("Cash-Only Check: Trade is 100% cash funded.")

        # 4. Shariah Screening
        if not is_shariah_compliant:
            violations.append(f"Compliance Violation: Asset '{ticker}' is flagged non-Shariah compliant.")
        else:
            passed_rules.append(f"Shariah Check: Asset '{ticker}' verified compliant.")

        # 5. Position Sizing Allocation
        if position_size_pct > self.max_position_size_pct:
            violations.append(f"Allocation Violation: Position size {position_size_pct}% exceeds max single position allocation of {self.max_position_size_pct}%.")
        else:
            passed_rules.append(f"Position Allocation Check: {position_size_pct}% <= {self.max_position_size_pct}% max size.")

        compliant = (len(violations) == 0)

        return {
            "component": "SKILL",
            "skill_name": self.name,
            "ticker": ticker,
            "compliant": compliant,
            "violations": violations,
            "passed_rules": passed_rules,
            "summary_status": "APPROVED" if compliant else "REJECTED",
            "metrics_checked": {
                "proposed_risk_pct": proposed_risk,
                "positions_today": positions_today,
                "is_cash_trade": is_cash_trade,
                "is_shariah_compliant": is_shariah_compliant,
                "position_size_pct": position_size_pct
            }
        }
