"""
Transaction Cost & Brokerage Model.
Calculates brokerage fees, STT, and exchange taxes per trade.
"""
class TransactionCostModel:
    def __init__(self, fixed_fee: float = 20.0, variable_rate: float = 0.0003):
        self.fixed_fee = fixed_fee
        self.variable_rate = variable_rate

    def calculate_cost(self, trade_value: float) -> float:
        return self.fixed_fee + (trade_value * self.variable_rate)
