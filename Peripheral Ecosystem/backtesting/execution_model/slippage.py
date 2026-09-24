"""
Slippage Modeling Contract.
Applies realistic price degradation based on volatility, volume, or fixed percentage.
"""
class SlippageModel:
    def __init__(self, slippage_pct: float = 0.0005):
        self.slippage_pct = slippage_pct

    def adjust_entry_price(self, target_price: float, direction: str) -> float:
        # Buy higher, sell lower due to slippage
        if direction.upper() == "BUY":
            return target_price * (1.0 + self.slippage_pct)
        else:
            return target_price * (1.0 - self.slippage_pct)
