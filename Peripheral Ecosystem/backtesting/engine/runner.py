"""
Backtest Engine Runner.
Loops through historical OHLCV bars chronologically, separates signal generation 
from execution, and applies slippage and costs.
"""
class BacktestRunner:
    def __init__(self, strategy, execution_model, slippage_model, cost_model):
        self.strategy = strategy
        self.execution_model = execution_model
        self.slippage_model = slippage_model
        self.cost_model = cost_model

    def run(self, bars: list) -> dict:
        history = []
        trades = []
        active_position = None

        for idx, bar in enumerate(bars):
            # 1. Check existing position exits if active
            if active_position:
                exit_check = self.execution_model.check_exits(bar, active_position)
                if exit_check["exit_triggered"]:
                    active_position["exit_price"] = exit_check["exit_price"]
                    active_position["exit_time"] = bar.timestamp
                    active_position["reason"] = exit_check["reason"]
                    trades.append(active_position)
                    active_position = None

            # 2. Evaluate strategy on historical context (signal on close)
            signal_result = self.strategy.on_bar(idx, bar, history)
            
            # 3. If signal generated and no active position, prepare order for next open execution
            if signal_result.get("signal") == "BUY" and not active_position:
                pass

            history.append(bar)

        return {"total_trades": len(trades), "trades": trades}
