"""
Unit Test Suite for Trade Attribution Engine (Phase C).
Validates known-answer fixtures, R-multiples, edge cases, and strict immutability.
"""
import unittest
import copy
import sys

sys.path.append(r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem")
from backtesting.Pillar4.analytics.attribution import TradeAttributionEngine

class TestTradeAttribution(unittest.TestCase):

    def setUp(self):
        self.sample_trades = [
            {
                "strategy_id": "SMA_Crossover_Parity",
                "symbol": "RELIANCE",
                "direction": "BUY",
                "entry_time": "2026-06-01 09:45:00",
                "entry_price": 2430.0,
                "stop_loss": 2380.0, # Risk = 50.0
                "target_price": 2480.0,
                "exit_time": "2026-06-01 10:15:00",
                "exit_price": 2375.0,
                "reason": "STOP_LOSS",
                "quantity": 100,
                "gross_pnl": -5500.0,
                "costs": 40.0,
                "net_pnl": -5540.0
            },
            {
                "strategy_id": "SMA_Crossover_Parity",
                "symbol": "TCS",
                "direction": "BUY",
                "entry_time": "2026-06-01 11:00:00",
                "entry_price": 3500.0,
                "stop_loss": 3450.0, # Risk = 50.0
                "target_price": 3600.0,
                "exit_time": "2026-06-01 12:00:00",
                "exit_price": 3600.0,
                "reason": "TAKE_PROFIT",
                "quantity": 50,
                "gross_pnl": 5000.0,
                "costs": 30.0,
                "net_pnl": 4970.0
            },
            {
                "strategy_id": "SMA_Crossover_Parity",
                "symbol": "INFY",
                "direction": "BUY",
                "entry_time": "2026-06-01 13:00:00",
                "entry_price": 1500.0,
                "stop_loss": 1500.0, # Zero risk edge case
                "target_price": 1550.0,
                "exit_time": "2026-06-01 13:30:00",
                "exit_price": 1510.0,
                "reason": "SIGNAL_EXIT",
                "quantity": 100,
                "gross_pnl": 1000.0,
                "costs": 20.0,
                "net_pnl": 980.0
            }
        ]

    def test_empty_input(self):
        self.assertEqual(TradeAttributionEngine.enrich_trades([]), [])

    def test_winning_and_losing_outcomes(self):
        enriched = TradeAttributionEngine.enrich_trades(self.sample_trades)
        # Trade 0: Loss (-5540.0 net pnl)
        self.assertEqual(enriched[0]["outcome"], "LOSS")
        self.assertTrue(enriched[0]["is_loser"])
        self.assertFalse(enriched[0]["is_winner"])
        
        # Trade 1: Win (4970.0 net pnl)
        self.assertEqual(enriched[1]["outcome"], "WIN")
        self.assertTrue(enriched[1]["is_winner"])
        self.assertFalse(enriched[1]["is_loser"])

    def test_r_multiple_calculation(self):
        enriched = TradeAttributionEngine.enrich_trades(self.sample_trades)
        # Trade 1 Risk = (3500 - 3450) * 50 = 50 * 50 = 2500. Net PnL = 4970. R = 4970 / 2500 = 1.988
        self.assertEqual(enriched[1]["r_multiple"], 1.988)
        # Trade 0 Risk = (2430 - 2380) * 100 = 5000. Net PnL = -5540. R = -5540 / 5000 = -1.108
        self.assertEqual(enriched[0]["r_multiple"], -1.108)

    def test_zero_initial_risk_handling(self):
        enriched = TradeAttributionEngine.enrich_trades(self.sample_trades)
        # Trade 2 has entry == stop_loss -> zero risk
        self.assertEqual(enriched[2]["initial_risk"], 0.0)
        self.assertEqual(enriched[2]["r_multiple"], 0.0)
        self.assertEqual(enriched[2]["risk_status"], "INVALID_OR_ZERO_RISK")

    def test_exit_classification(self):
        enriched = TradeAttributionEngine.enrich_trades(self.sample_trades)
        self.assertEqual(enriched[0]["exit_classification"], "STOP_LOSS_HIT")
        self.assertEqual(enriched[1]["exit_classification"], "TAKE_PROFIT_HIT")
        self.assertEqual(enriched[2]["exit_classification"], "MANUAL_OR_SIGNAL_EXIT")

    def test_chronological_ordering_and_preservation(self):
        enriched = TradeAttributionEngine.enrich_trades(self.sample_trades)
        self.assertEqual(len(enriched), 3)
        self.assertEqual(enriched[0]["symbol"], "RELIANCE")
        self.assertEqual(enriched[1]["symbol"], "TCS")
        self.assertEqual(enriched[2]["symbol"], "INFY")

    def test_input_immutability(self):
        """Proves that input certified trade dictionaries remain 100% unchanged after enrichment."""
        original_snapshot = copy.deepcopy(self.sample_trades)
        _ = TradeAttributionEngine.enrich_trades(self.sample_trades)
        self.assertEqual(self.sample_trades, original_snapshot, "Immutability violated: original certified trades were modified.")

if __name__ == "__main__":
    unittest.main()
