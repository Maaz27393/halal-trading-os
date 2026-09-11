from typing import Dict, Any, List, Callable, Optional
from paper_trading_harness import PaperTradingHarness
from historical_data_adapter import HistoricalDataAdapter

class StrategyBacktestRunner:
    """
    Phase 10B: Strategy Backtest Runner
    Drives historical candle streams through the Phase 9 Paper Trading Harness,
    executing signal evaluation and capturing real-time equity time-series.
    """
    def __init__(self, initial_capital: float = 200000.0, max_slippage_pct: float = 0.5):
        self.initial_capital = initial_capital
        self.harness = PaperTradingHarness(initial_capital=initial_capital, max_slippage_pct=max_slippage_pct)
        self.equity_curve: List[Dict[str, Any]] = []
        self.trade_logs: List[Dict[str, Any]] = []

    def run(self, candle_feed: List[Dict[str, Any]], signal_evaluator: Callable[[Dict[str, Any], Dict[str, Any]], Optional[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Iterates over historical candles sequentially.
        - candle_feed: Chronologically sorted list of candles.
        - signal_evaluator: Function receiving (candle, current_portfolio_summary) -> returns trade signal or None.
        """
        signals_generated = 0
        executed_trades = 0

        for candle in candle_feed:
            ticker = candle["ticker"]
            timestamp = candle["timestamp_epoch"]

            # Update MTM prices for signal evaluation
            portfolio_summary = self.harness.update_portfolio({ticker: candle["close"]})

            # Evaluate strategy rules
            signal = signal_evaluator(candle, portfolio_summary)
            if signal:
                signals_generated += 1
                res = self.harness.process_trade_signal(signal, candle)
                if res["status"] in ["FILLED", "PARTIALLY_FILLED"]:
                    executed_trades += 1
                    self.trade_logs.append({
                        "timestamp_epoch": timestamp,
                        "signal": signal,
                        "execution_result": res
                    })
                # Re-sync portfolio state after trade fill
                portfolio_summary = self.harness.update_portfolio({ticker: candle["close"]})

            # Record point-in-time equity post-execution
            self.equity_curve.append({
                "timestamp_epoch": timestamp,
                "ticker": ticker,
                "total_equity": portfolio_summary["total_equity"],
                "available_capital": portfolio_summary["available_capital"],
                "unrealized_pnl": portfolio_summary["total_unrealized_pnl"],
                "realized_pnl": portfolio_summary["total_realized_pnl"]
            })

        final_summary = self.harness.position_engine.get_portfolio_summary()

        return {
            "candles_processed": len(candle_feed),
            "signals_generated": signals_generated,
            "executed_trades": executed_trades,
            "final_portfolio": final_summary,
            "equity_curve": self.equity_curve,
            "trade_logs": self.trade_logs
        }
