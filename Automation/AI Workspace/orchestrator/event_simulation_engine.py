from typing import Dict, Any, Tuple

class EventSimulationEngine:
    """
    Phase 10C: Event Simulation Engine
    Simulates real-world market stress conditions and friction during backtesting:
    - Price Gaps (Overnight/News)
    - Circuit Breakers / Trading Halts
    - Volume-Capped Partial Fills
    - Volatility Slippage Spikes
    """
    def __init__(self, circuit_limit_pct: float = 10.0, max_volume_participation_pct: float = 0.10):
        self.circuit_limit_pct = circuit_limit_pct
        self.max_volume_participation_pct = max_volume_participation_pct

    def check_circuit_breaker(self, candle: Dict[str, Any], reference_close: float) -> bool:
        """Determines if the current candle violates the daily circuit breaker limit."""
        if reference_close <= 0:
            return False
        price_change_pct = abs((candle["close"] - reference_close) / reference_close) * 100.0
        return price_change_pct >= self.circuit_limit_pct

    def apply_price_gap(self, candle: Dict[str, Any], gap_pct: float) -> Dict[str, Any]:
        """Injects a gapped opening price into a candle."""
        gapped = candle.copy()
        factor = 1.0 + (gap_pct / 100.0)
        gapped["open"] = round(candle["open"] * factor, 2)
        gapped["high"] = max(gapped["high"], gapped["open"])
        gapped["low"] = min(gapped["low"], gapped["open"])
        gapped["close"] = round(candle["close"] * factor, 2)
        gapped["ask"] = round(candle["ask"] * factor, 2)
        gapped["bid"] = round(candle["bid"] * factor, 2)
        return gapped

    def calculate_volume_fill(self, requested_qty: int, candle_volume: int) -> Tuple[int, bool]:
        """
        Caps order fill quantity based on participation rate relative to bar volume.
        Returns (fillable_qty, is_partial_fill).
        """
        max_fillable = int(candle_volume * self.max_volume_participation_pct)
        if max_fillable <= 0:
            return 0, True
        if requested_qty <= max_fillable:
            return requested_qty, False
        return max_fillable, True

    def calculate_stress_slippage(self, base_price: float, side: str, volatility_multiplier: float = 1.0, base_slippage_pct: float = 0.05) -> float:
        """Calculates execution price under high-volatility slippage conditions."""
        total_slippage_pct = base_slippage_pct * volatility_multiplier
        slippage_amt = base_price * (total_slippage_pct / 100.0)
        if side.upper() == "BUY":
            return round(base_price + slippage_amt, 2)
        return round(base_price - slippage_amt, 2)
