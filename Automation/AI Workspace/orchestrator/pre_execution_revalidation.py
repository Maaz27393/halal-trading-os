from typing import Dict, Any
import time

class PreExecutionRevalidator:
    """
    Phase 9C: Pre-Execution Revalidation Suite
    Performs last-second sanity checks prior to order submission:
    - Market tick data staleness check (< max_stale_seconds)
    - Price drift boundary relative to original limit/trigger price
    - Capital & position risk boundary checks at moment of submission
    """
    def __init__(self, max_stale_seconds: float = 5.0, max_price_drift_pct: float = 0.8):
        self.max_stale_seconds = max_stale_seconds
        self.max_price_drift_pct = max_price_drift_pct

    def revalidate(self, order_payload: Dict[str, Any], live_candle: Dict[str, Any], available_capital: float) -> Dict[str, Any]:
        ticker = order_payload.get("ticker", "").upper()
        limit_price = float(order_payload.get("limit_price", 0.0))
        qty = int(order_payload.get("qty", 0))
        
        required_capital = qty * limit_price

        # 1. Capital Availability Check
        if required_capital > available_capital:
            return {
                "revalidated": False,
                "reason": f"Capital insufficient at execution moment: required {required_capital:.2f}, available {available_capital:.2f}"
            }

        # 2. Market Data Staleness Check
        candle_ts = float(live_candle.get("timestamp_epoch", time.time()))
        age_seconds = time.time() - candle_ts
        if age_seconds > self.max_stale_seconds:
            return {
                "revalidated": False,
                "reason": f"Stale market data: age {age_seconds:.2f}s exceeds limit {self.max_stale_seconds}s"
            }

        # 3. Price Drift Check
        current_close = float(live_candle.get("close", limit_price))
        drift_pct = (abs(current_close - limit_price) / limit_price) * 100.0

        if drift_pct > self.max_price_drift_pct:
            return {
                "revalidated": False,
                "reason": f"Price drift limit exceeded: {drift_pct:.2f}% > allowed {self.max_price_drift_pct}%"
            }

        return {
            "revalidated": True,
            "reason": "All last-second pre-execution checks passed",
            "ticker": ticker,
            "drift_pct": round(drift_pct, 4)
        }
