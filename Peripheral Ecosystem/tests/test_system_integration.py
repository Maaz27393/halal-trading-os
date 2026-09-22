import unittest
import sys
import os

# Set path to Peripheral Ecosystem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtesting.engine.backtest_engine import BacktestEngine
from backtesting.contracts.backtest_contract import TradeSignal, TradeResult, BacktestReport

class TestSystemIntegrationReadiness(unittest.TestCase):
    
    def test_governance_and_execution_boundary(self):
        """Validates that all domains strictly enforce non-execution governance."""
        engine = BacktestEngine(initial_capital=50000.0)
        self.assertFalse(engine.live_auto_execution, "CRITICAL: Backtest engine violated non-execution policy!")

    def test_canonical_contracts_integrity(self):
        """Validates that contracts initialize correctly without domain coupling."""
        signal = TradeSignal(
            symbol="RELIANCE",
            entry_time="2026-09-20T10:00:00Z",
            entry_price=2500.0,
            direction="LONG",
            stop_loss=2450.0,
            target_price=2600.0
        )
        self.assertEqual(signal.symbol, "RELIANCE")
        self.assertEqual(signal.direction, "LONG")

if __name__ == "__main__":
    unittest.main()
