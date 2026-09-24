"""
Stop Loss and Take Profit Exit Evaluation Contract.
Evaluates intraday or daily high/low bars against active stop loss and target prices.
"""
class ExitModel:
    @staticmethod
    def check_exits(bar, position) -> dict:
        result = {"exit_triggered": False, "exit_price": 0.0, "reason": None}
        if position.direction == "BUY":
            if bar.low <= position.stop_loss:
                result = {"exit_triggered": True, "exit_price": position.stop_loss, "reason": "STOP_LOSS"}
            elif bar.high >= position.target_price:
                result = {"exit_triggered": True, "exit_price": position.target_price, "reason": "TAKE_PROFIT"}
        return result
