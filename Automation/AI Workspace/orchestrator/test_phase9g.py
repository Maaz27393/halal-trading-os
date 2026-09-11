import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from paper_trading_harness import PaperTradingHarness

def run_phase9g_tests():
    print("=== STARTING PHASE 9G: END-TO-END PAPER TRADING HARNESS TESTS ===")
    harness = PaperTradingHarness(initial_capital=200000.0)

    now = time.time()

    # Test 1: Complete End-to-End Buy Signal Processing
    signal1 = {"ticker": "TATAMOTORS", "side": "BUY", "qty": 50, "limit_price": 980.0}
    candle1 = {"close": 981.0, "ask": 981.0, "bid": 980.5, "volume": 500, "timestamp_epoch": now}

    res1 = harness.process_trade_signal(signal1, candle1)
    assert res1["status"] == "FILLED"
    assert res1["order"]["state"] == "FILLED"
    assert res1["audit"]["status"] == "RECONCILED_MATCH"
    assert "TATAMOTORS" in harness.position_engine.positions
    print("[PASS] Test 1 | Full End-to-End Buy Order Processing & Position Sync Verified")

    # Test 2: Portfolio Mark-to-Market Accounting Integration
    summary = harness.update_portfolio({"TATAMOTORS": 1010.0})
    assert summary["open_positions_count"] == 1
    assert summary["total_unrealized_pnl"] > 0
    print("[PASS] Test 2 | Real-time Portfolio MTM Calculation Verified")

    # Test 3: Rejection on Price Drift Violation Integration
    signal2 = {"ticker": "INFY", "side": "BUY", "qty": 20, "limit_price": 1500.0}
    candle2 = {"close": 1525.0, "ask": 1525.0, "bid": 1524.0, "volume": 500, "timestamp_epoch": now} # 1.67% drift > 0.8%

    res2 = harness.process_trade_signal(signal2, candle2)
    assert res2["status"] == "REJECTED"
    assert res2["order"]["state"] == "REJECTED"
    assert "Price drift limit exceeded" in res2["reason"]
    assert "INFY" not in harness.position_engine.positions
    print("[PASS] Test 3 | End-to-End Revalidation Interception Verified")

    # Test 4: Complete Round-Trip Trade Execution (Buy -> Profit Sell)
    signal3 = {"ticker": "TATAMOTORS", "side": "SELL", "qty": 50, "limit_price": 1005.0}
    candle3 = {"close": 1010.0, "ask": 1010.5, "bid": 1010.0, "volume": 500, "timestamp_epoch": now}

    res3 = harness.process_trade_signal(signal3, candle3)
    assert res3["status"] == "FILLED"
    assert res3["audit"]["status"] == "RECONCILED_MATCH"
    assert res3["audit"]["realized_pnl"] > 0
    assert "TATAMOTORS" not in harness.position_engine.positions
    print("[PASS] Test 4 | Complete Round-Trip Execution & Profit Realization Verified")

    print("\nPhase 9G End-to-End Paper Trading Harness Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase9g_tests()
