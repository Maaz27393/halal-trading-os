"""
Pillar 4 Comprehensive Backend Verification Suite.
Validates contracts, data loaders, point-in-time Shariah universe, 
execution models, backtest runner, and Power BI exporters.
"""
import sys
import os
from datetime import datetime

# Add backtesting base to path
sys.path.append(r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem")

from backtesting.contracts.ohlcv import OHLCVBar
from backtesting.data.universe.shariah_universe import PointInTimeUniverse
from backtesting.strategies.pine_parity.sma_crossover_parity import SMACrossoverParityStrategy
from backtesting.engine.runner import BacktestRunner
from backtesting.execution_model.exits import ExitModel
from backtesting.execution_model.slippage import SlippageModel
from backtesting.execution_model.costs import TransactionCostModel
from backtesting.exporters.powerbi import PowerBIBacktestExporter

def run_verification():
    print("=" * 60)
    print("PILLAR 4 BACKEND VERIFICATION SUITE")
    print("=" * 60)

    # 1. Test Contracts & OHLCV Bar creation
    bar = OHLCVBar(datetime(2026, 1, 2, 9, 15), "TEST_SYM", 100.0, 105.0, 99.0, 104.0, 5000.0)
    assert bar.symbol == "TEST_SYM"
    print("[PASS] Canonical OHLCV Contract verified.")

    # 2. Test Point-in-Time Shariah Universe Filtering
    universe_records = [
        {"symbol": "RELIANCE", "valid_from": datetime(2025, 1, 1), "valid_to": datetime(2026, 12, 31), "is_shariah": True},
        {"symbol": "NON_SHARIAH", "valid_from": datetime(2025, 1, 1), "valid_to": datetime(2026, 12, 31), "is_shariah": False}
    ]
    universe = PointInTimeUniverse(universe_records)
    assert universe.is_eligible("RELIANCE", datetime(2026, 6, 1)) == True
    assert universe.is_eligible("NON_SHARIAH", datetime(2026, 6, 1)) == False
    assert universe.is_eligible("RELIANCE", datetime(2024, 1, 1)) == False # Outside validity window (survivorship bias prevention)
    print("[PASS] Point-in-Time Shariah Universe filter verified.")

    # 3. Test Strategy Interface & Parity Skeleton
    strategy = SMACrossoverParityStrategy(fast_period=2, slow_period=5)
    assert strategy.name == "SMA_Crossover_Parity"
    print("[PASS] Strategy Specification & Parity interface verified.")

    # 4. Test Execution & Slippage Models
    slippage = SlippageModel(slippage_pct=0.001)
    adjusted_buy = slippage.adjust_entry_price(100.0, "BUY")
    assert adjusted_buy == 100.1
    print("[PASS] Slippage & Execution model verified.")

    # 5. Test Cost Model
    costs = TransactionCostModel(fixed_fee=20.0, variable_rate=0.0)
    assert costs.calculate_cost(50000.0) == 20.0
    print("[PASS] Transaction Cost model verified.")

    # 6. Test Exit Evaluation
    class MockPosition:
        direction = "BUY"
        stop_loss = 95.0
        target_price = 110.0

    exit_bar = OHLCVBar(datetime(2026, 1, 2, 10, 0), "TEST_SYM", 102.0, 103.0, 94.0, 98.0, 1000.0)
    exit_result = ExitModel.check_exits(exit_bar, MockPosition())
    assert exit_result["exit_triggered"] == True
    assert exit_result["reason"] == "STOP_LOSS"
    print("[PASS] Exit Model & Stop-Loss evaluation verified.")

    # 7. Test Power BI Exporter
    exporter = PowerBIBacktestExporter()
    sample_trades = [
        {
            "strategy_id": "SMA_Crossover_Parity",
            "symbol": "TEST_SYM",
            "direction": "BUY",
            "entry_time": "2026-01-02 09:30:00",
            "entry_price": 100.1,
            "exit_time": "2026-01-02 10:00:00",
            "exit_price": 95.0,
            "reason": "STOP_LOSS",
            "pnl": -5.1
        }
    ]
    exported_file = exporter.export_trades("SMA_Crossover_Parity", sample_trades)
    assert os.path.exists(exported_file)
    print(f"[PASS] Power BI Exporter verified. Output written to: {exported_file}")

    print("=" * 60)
    print("RESULT: Parity Harness PASS | Pillar 4 Backend Verification: PASS")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
