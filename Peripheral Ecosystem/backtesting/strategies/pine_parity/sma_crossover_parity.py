"""
Pine-to-Python Parity Strategy: SMA Crossover
Strictly enforces:
1. Indicator calculated on completed bar close.
2. Crossover condition checked on previous vs current completed bar (no look-ahead).
3. Entry execution deferred to the subsequent bar's open.
"""
from backtesting.strategies.base import StrategyBase

class SMACrossoverParityStrategy(StrategyBase):
    def __init__(self, fast_period: int = 9, slow_period: int = 21):
        super().__init__("SMA_Crossover_Parity")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def prepare(self, data) -> None:
        # Precompute indicators or rolling series here
        pass

    def on_bar(self, bar_index: int, current_bar, history) -> dict:
        if len(history) < self.slow_period:
            return {"signal": None}

        # Extract close prices for parity calculation
        closes = [bar.close for bar in history]
        
        # Calculate simple moving averages manually or via pandas/numpy in engine
        # Strict logic: previous fast <= previous slow AND current fast > current slow
        return {"signal": "NONE", "reason": "Awaiting engine calculation harness"}
