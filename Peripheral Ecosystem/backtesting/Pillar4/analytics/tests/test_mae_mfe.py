"""
Unit Test Suite for Trade Metrics (MAE & MFE).
Validates excursion calculations using simulated intrabar price bars.
"""
import unittest
from datetime import datetime
import sys

sys.path.append(r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem")
from backtesting.contracts.ohlcv import OHLCVBar
from backtesting.Pillar4.analytics.metrics import TradeMetricsEngine

class TestTradeMetrics(unittest.TestCase):

    def setUp(self):
        self.bars = [
            OHLCVBar(datetime(2026, 6, 1, 9, 45), "RELIANCE", 2430.0, 2450.0, 2410.0, 2440.0, 1000),
            OHLCVBar(datetime(2026, 6, 1, 10, 00), "RELIANCE", 2440.0, 2465.0, 2420.0, 2460.0, 1200),
            OHLCVBar(datetime(2026, 6, 1, 10, 15), "RELIANCE", 2460.0, 2460.0, 2375.0, 2380.0, 1500)
        ]

    def test_buy_mae_mfe_calculation(self):
        trade = {
            "direction": "BUY",
            "entry_time": "2026-06-01 09:45:00",
            "exit_time": "2026-06-01 10:15:00",
            "entry_price": 2430.0
        }
        excursions = TradeMetricsEngine.calculate_excursions(trade, self.bars)
        
        # For BUY at 2430:
        # Lowest low across bars = 2375 -> MAE abs = 2430 - 2375 = 55.0
        # Highest high across bars = 2465 -> MFE abs = 2465 - 2430 = 35.0
        self.assertEqual(excursions["mae_abs"], 55.0)
        self.assertEqual(excursions["mfe_abs"], 35.0)
        self.assertGreater(excursions["mae_pct"], 0.0)
        self.assertGreater(excursions["mfe_pct"], 0.0)

    def test_empty_bars_handling(self):
        trade = {
            "direction": "BUY",
            "entry_time": "2026-06-02 09:45:00",
            "exit_time": "2026-06-02 10:15:00",
            "entry_price": 2430.0
        }
        excursions = TradeMetricsEngine.calculate_excursions(trade, self.bars)
        self.assertEqual(excursions["mae_abs"], 0.0)
        self.assertEqual(excursions["mfe_abs"], 0.0)

if __name__ == "__main__":
    unittest.main()
