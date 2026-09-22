import unittest
from datetime import datetime, timezone
from backtesting.contracts.backtest_contract import OHLCVBar, TradeSignal
from backtesting.engine.backtest_engine import BacktestEngine

class TestBacktestingDomain(unittest.TestCase):
    def test_backtest_simulation_target_hit(self):
        # Set a realistic brokerage fee for a 100-unit trade
        engine = BacktestEngine(initial_capital=100000.0, brokerage_fee=1.0)
        self.assertFalse(engine.live_auto_execution)

        bars = [
            OHLCVBar(timestamp=datetime(2026, 9, 20, 9, 15, tzinfo=timezone.utc), open=100, high=105, low=98, close=102, volume=1000),
            OHLCVBar(timestamp=datetime(2026, 9, 20, 9, 30, tzinfo=timezone.utc), open=102, high=112, low=101, close=110, volume=1500)
        ]

        signal = TradeSignal(
            symbol="RELIANCE",
            entry_time=datetime(2026, 9, 20, 9, 15, tzinfo=timezone.utc),
            entry_price=100.0,
            direction="LONG",
            stop_loss=95.0,
            target_price=110.0
        )

        report = engine.run_simulation("BreakoutStrategy", "RELIANCE", bars, signal)
        self.assertEqual(report.strategy_name, "BreakoutStrategy")
        self.assertEqual(report.total_trades, 1)
        self.assertEqual(report.winning_trades, 1)
        self.assertEqual(report.trades[0].outcome, "TARGET_HIT")

if __name__ == "__main__":
    unittest.main()
