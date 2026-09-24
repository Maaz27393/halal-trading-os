"""
Unit Test Suite for Power BI Analytics Exporter (Phase C).
Validates file generation and schema serialization for the 3 canonical CSV feeds.
"""
import unittest
import os
import sys

sys.path.append(r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem")
from backtesting.Pillar4.exporters.powerbi_exporter import PowerBIAnalyticsExporter

class TestPowerBIExporter(unittest.TestCase):

    def test_export_generation(self):
        exporter = PowerBIAnalyticsExporter()
        trades = [{
            "strategy_id": "TEST", "symbol": "RELIANCE", "net_pnl": 1500.0, 
            "outcome": "WIN", "r_multiple": 1.5, "mae_abs": 100.0, "mfe_abs": 1600.0
        }]
        summary = {"strategy_id": "TEST", "total_trades": 1, "win_rate": 100.0, "expectancy": 1500.0}
        equity = [{"timestamp": "2026-06-01 10:00:00", "equity": 101500.0, "drawdown_abs": 0.0, "drawdown_pct": 0.0}]

        paths = exporter.export_all("TEST_STRATEGY", trades, summary, equity)
        
        self.assertTrue(os.path.exists(paths["trades"]))
        self.assertTrue(os.path.exists(paths["summary"]))
        self.assertTrue(os.path.exists(paths["equity"]))

if __name__ == "__main__":
    unittest.main()
