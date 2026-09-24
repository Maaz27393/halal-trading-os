"""
Unit Test Suite for Portfolio Drawdown Engine (Phase C).
Validates running peaks, drawdown tracking, and max drawdown metrics.
"""
import unittest
import sys

sys.path.append(r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem")
from backtesting.Pillar4.analytics.drawdown import DrawdownEngine

class TestDrawdownEngine(unittest.TestCase):

    def test_drawdown_calculation_with_trades(self):
        initial_capital = 100000.0
        trades = [
            {"entry_time": "2026-06-01 09:45:00", "exit_time": "2026-06-01 10:15:00", "net_pnl": 5000.0},   # Equity: 105,000 | Peak: 105,000
            {"entry_time": "2026-06-01 10:30:00", "exit_time": "2026-06-01 11:00:00", "net_pnl": -10000.0},  # Equity: 95,000  | Peak: 105,000 | DD: 10,000 (9.52%)
            {"entry_time": "2026-06-01 11:15:00", "exit_time": "2026-06-01 12:00:00", "net_pnl": 15000.0}    # Equity: 110,000 | Peak: 110,000
        ]

        result = DrawdownEngine.compute_equity_curve(initial_capital, trades)
        self.assertEqual(result["final_equity"], 110000.0)
        self.assertEqual(result["max_drawdown_abs"], 10000.0)
        self.assertAlmostEqual(result["max_drawdown_pct"], 9.5238, places=3)
        self.assertEqual(len(result["equity_curve"]), 4)

    def test_empty_trades(self):
        result = DrawdownEngine.compute_equity_curve(100000.0, [])
        self.assertEqual(result["final_equity"], 100000.0)
        self.assertEqual(result["max_drawdown_abs"], 0.0)
        self.assertEqual(result["equity_curve"], [])

if __name__ == "__main__":
    unittest.main()
