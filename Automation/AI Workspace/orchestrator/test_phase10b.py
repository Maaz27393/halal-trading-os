import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from historical_data_adapter import HistoricalDataAdapter
from strategy_backtest_runner import StrategyBacktestRunner

def run_phase10b_tests():
    print("=== STARTING PHASE 10B: STRATEGY BACKTEST RUNNER TESTS ===")

    adapter = HistoricalDataAdapter(default_spread_pct=0.05)
    now = int(time.time())

    # Mock historical candle series simulating a profitable breakout trade
    raw_data = [
        {"timestamp_epoch": now, "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 1000},
        {"timestamp_epoch": now + 60, "open": 101.0, "high": 108.0, "low": 100.5, "close": 107.0, "volume": 5000}, # Breakout -> BUY @ ~107
        {"timestamp_epoch": now + 120, "open": 107.0, "high": 115.0, "low": 106.0, "close": 114.0, "volume": 3000},
        {"timestamp_epoch": now + 180, "open": 114.0, "high": 114.0, "low": 108.0, "close": 109.0, "volume": 4000}  # Target/Trailing exit -> SELL @ ~109 (> 107)
    ]

    candle_feed = adapter.normalize_candles(raw_data, "TATAMOTORS")

    def dummy_breakout_strategy(candle, portfolio):
        # Entry rule: Close > 105 and no open position
        if candle["close"] > 105.0 and portfolio["open_positions_count"] == 0:
            return {"ticker": candle["ticker"], "side": "BUY", "qty": 100, "limit_price": candle["close"]}
        # Exit rule: Close < 110 and open position exists
        elif candle["close"] < 110.0 and portfolio["open_positions_count"] > 0:
            return {"ticker": candle["ticker"], "side": "SELL", "qty": 100, "limit_price": candle["close"]}
        return None

    runner = StrategyBacktestRunner(initial_capital=200000.0)
    result = runner.run(candle_feed, dummy_breakout_strategy)

    # Test 1: Complete Stream Processing & Signal Tracking
    assert result["candles_processed"] == 4
    assert result["signals_generated"] == 2
    assert result["executed_trades"] == 2
    print("[PASS] Test 1 | Historical Stream Execution & Signal Tracking Verified")

    # Test 2: Equity Curve Point-in-Time Generation
    assert len(result["equity_curve"]) == 4
    assert result["equity_curve"][-1]["total_equity"] > 200000.0 # Profitable trade
    print("[PASS] Test 2 | Point-in-Time Equity Time-Series Generation Verified")

    # Test 3: Round-Trip Realized Profit Verification
    assert result["final_portfolio"]["open_positions_count"] == 0
    assert result["final_portfolio"]["total_realized_pnl"] > 0
    print("[PASS] Test 3 | Backtest Round-Trip PnL Reconciliation Verified")

    print("\nPhase 10B Strategy Backtest Runner Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase10b_tests()
