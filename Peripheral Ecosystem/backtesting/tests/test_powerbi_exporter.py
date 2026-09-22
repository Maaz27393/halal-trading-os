import unittest
from datetime import datetime, timezone
from backtesting.contracts.backtest_contract import TradeResult, BacktestReport
from backtesting.exporters.powerbi_lifecycle_exporter import OpportunityLifecyclePowerBIExporter

class TestPowerBILifecycleExporter(unittest.TestCase):
    def test_powerbi_flattening(self):
        exporter = OpportunityLifecyclePowerBIExporter()
        self.assertFalse(exporter.live_auto_execution)

        result = TradeResult(
            symbol="TCS",
            entry_time=datetime(2026, 9, 20, 9, 30, tzinfo=timezone.utc),
            exit_time=datetime(2026, 9, 20, 10, 30, tzinfo=timezone.utc),
            entry_price=3500.0,
            exit_price=3570.0,
            direction="LONG",
            pnl=68.0,
            pnl_percentage=1.94,
            outcome="TARGET_HIT"
        )

        report = BacktestReport(
            strategy_name="IntradayMomentum",
            total_trades=1,
            winning_trades=1,
            losing_trades=0,
            win_rate=100.0,
            net_pnl=68.0,
            max_drawdown=0.0,
            trades=[result]
        )

        rows = exporter.export_lifecycle_to_table([report])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["StrategyName"], "IntradayMomentum")
        self.assertEqual(rows[0]["Symbol"], "TCS")
        self.assertEqual(rows[0]["IsSuccessful"], 1)

if __name__ == "__main__":
    unittest.main()
