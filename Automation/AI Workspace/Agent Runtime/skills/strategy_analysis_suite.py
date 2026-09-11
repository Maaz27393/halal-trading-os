from typing import Dict, Any, List

class StrategyAnalysisSuite:
    """
    Phase 7B Skill: Strategy Analysis Suite
    Validates technical setups against core strategy criteria:
    - EMA Trend Alignment (EMA20 > EMA50 for Long)
    - EMA20 Pullback Proximity (Price within 1.5% of EMA20)
    - VWAP Alignment (Price >= VWAP for Long)
    - RSI Momentum/Pullback Zone (RSI between 40 and 65)
    - Risk-to-Reward Ratio (>= 1.5)
    """
    def __init__(self, name: str = "StrategyAnalysisSuite"):
        self.name = name
        self.min_rr_ratio = 1.5

    def execute(self, context: Any = None, **kwargs) -> Dict[str, Any]:
        data = {}
        if isinstance(context, dict):
            data.update(context)
        data.update(kwargs)

        ticker = data.get("ticker", "UNKNOWN")
        strategy_name = data.get("strategy_name", "EMA_PULLBACK")
        close_price = float(data.get("close_price", 0.0))
        ema20 = float(data.get("ema20", 0.0))
        ema50 = float(data.get("ema50", 0.0))
        vwap = float(data.get("vwap", 0.0))
        rsi = float(data.get("rsi", 50.0))
        risk_reward = float(data.get("risk_reward_ratio", 0.0))

        passed_checks: List[str] = []
        failed_checks: List[str] = []

        # 1. EMA Trend Alignment
        if ema20 > ema50:
            passed_checks.append(f"Trend Alignment: EMA20 ({ema20}) > EMA50 ({ema50}) confirms bullish alignment.")
        else:
            failed_checks.append(f"Trend Alignment Failure: EMA20 ({ema20}) <= EMA50 ({ema50}).")

        # 2. Price vs EMA20 Pullback Proximity
        if close_price > 0 and ema20 > 0:
            distance_pct = abs(close_price - ema20) / ema20 * 100
            if distance_pct <= 1.5:
                passed_checks.append(f"Pullback Proximity: Price ({close_price}) is within {distance_pct:.2f}% of EMA20 ({ema20}).")
            else:
                failed_checks.append(f"Pullback Proximity Failure: Price ({close_price}) is {distance_pct:.2f}% away from EMA20 ({ema20}) (max 1.5%).")

        # 3. VWAP Alignment
        if close_price >= vwap:
            passed_checks.append(f"VWAP Alignment: Price ({close_price}) >= VWAP ({vwap}).")
        else:
            failed_checks.append(f"VWAP Alignment Failure: Price ({close_price}) < VWAP ({vwap}).")

        # 4. RSI Range
        if 40.0 <= rsi <= 65.0:
            passed_checks.append(f"RSI Filter: RSI ({rsi}) is in optimal pullback zone (40-65).")
        else:
            failed_checks.append(f"RSI Filter Failure: RSI ({rsi}) outside optimal zone (40-65).")

        # 5. Risk-Reward Ratio
        if risk_reward >= self.min_rr_ratio:
            passed_checks.append(f"Risk-Reward: R:R ratio {risk_reward} meets minimum target ({self.min_rr_ratio}).")
        else:
            failed_checks.append(f"Risk-Reward Failure: R:R ratio {risk_reward} < required {self.min_rr_ratio}.")

        valid_setup = (len(failed_checks) == 0)

        return {
            "component": "SKILL",
            "skill_name": self.name,
            "ticker": ticker,
            "strategy_name": strategy_name,
            "valid_setup": valid_setup,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "summary_status": "VALID_SETUP" if valid_setup else "INVALID_SETUP",
            "technical_metrics": {
                "close_price": close_price,
                "ema20": ema20,
                "ema50": ema50,
                "vwap": vwap,
                "rsi": rsi,
                "risk_reward_ratio": risk_reward
            }
        }
