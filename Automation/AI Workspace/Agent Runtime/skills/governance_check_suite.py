from typing import Dict, Any, List

class GovernanceCheckSuite:
    """
    Phase 7D Skill: Governance & Conflict Check Suite
    Enforces macro-level operational governance and system circuit breakers:
    - Blacklist / Restricted Sector Check
    - Event Window Lock (e.g. Earnings within 48 hours)
    - System Circuit Breaker (Max Portfolio Drawdown <= 5.0%, Consecutive Losses < 3)
    - Directional / Order Conflict Check (No opposing open orders)
    """
    def __init__(self, name: str = "GovernanceCheckSuite"):
        self.name = name
        self.max_portfolio_drawdown_pct = 5.0
        self.max_consecutive_losses = 3

    def execute(self, context: Any = None, **kwargs) -> Dict[str, Any]:
        data = {}
        if isinstance(context, dict):
            data.update(context)
        data.update(kwargs)

        ticker = data.get("ticker", "UNKNOWN")
        is_blacklisted = bool(data.get("is_blacklisted", False))
        earnings_within_48h = bool(data.get("earnings_within_48h", False))
        portfolio_drawdown_pct = float(data.get("portfolio_drawdown_pct", 0.0))
        consecutive_losses = int(data.get("consecutive_losses", 0))
        has_conflicting_order = bool(data.get("has_conflicting_order", False))

        violations: List[str] = []
        passed_checks: List[str] = []

        # 1. Blacklist / Restricted Asset Check
        if is_blacklisted:
            violations.append(f"Blacklist Intercept: Asset '{ticker}' is on the restricted/blacklisted list.")
        else:
            passed_checks.append(f"Blacklist Check: Asset '{ticker}' cleared.")

        # 2. Event Window Lock
        if earnings_within_48h:
            violations.append(f"Event Lock: Asset '{ticker}' has high-volatility earnings release within 48h.")
        else:
            passed_checks.append(f"Event Window Check: No blackout earnings events within 48h.")

        # 3. System Circuit Breakers
        if portfolio_drawdown_pct >= self.max_portfolio_drawdown_pct:
            violations.append(f"Circuit Breaker: Portfolio drawdown ({portfolio_drawdown_pct}%) >= max threshold ({self.max_portfolio_drawdown_pct}%). Trading paused.")
        else:
            passed_checks.append(f"Drawdown Check: {portfolio_drawdown_pct}% < {self.max_portfolio_drawdown_pct}% cap.")

        if consecutive_losses >= self.max_consecutive_losses:
            violations.append(f"Circuit Breaker: Consecutive losses today ({consecutive_losses}) >= limit ({self.max_consecutive_losses}). Cooldown active.")
        else:
            passed_checks.append(f"Loss Streak Check: {consecutive_losses}/{self.max_consecutive_losses} consecutive losses.")

        # 4. Conflicting Order Check
        if has_conflicting_order:
            violations.append(f"Conflict Intercept: Existing pending or opposite open order detected for '{ticker}'.")
        else:
            passed_checks.append(f"Order Conflict Check: No opposing orders active for '{ticker}'.")

        governance_cleared = (len(violations) == 0)

        return {
            "component": "SKILL",
            "skill_name": self.name,
            "ticker": ticker,
            "governance_cleared": governance_cleared,
            "violations": violations,
            "passed_checks": passed_checks,
            "summary_status": "CLEARED" if governance_cleared else "GOVERNANCE_BLOCKED",
            "governance_metrics": {
                "is_blacklisted": is_blacklisted,
                "earnings_within_48h": earnings_within_48h,
                "portfolio_drawdown_pct": portfolio_drawdown_pct,
                "consecutive_losses": consecutive_losses,
                "has_conflicting_order": has_conflicting_order
            }
        }
