import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from position_state_engine import PositionStateEngine

def run_phase9b_tests():
    print("=== STARTING PHASE 9B: POSITION STATE ENGINE TESTS ===")
    engine = PositionStateEngine(initial_capital=100000.0)

    # Test 1: Successful Position Allocation
    res1 = engine.open_position(ticker="TATAMOTORS", qty=50, entry_price=900.0, stop_loss=870.0, target_price=960.0)
    assert res1["success"] is True
    assert engine.available_capital == 55000.0 # 100,000 - 45,000
    print("[PASS] Test 1 | Capital Allocation & Long Position Creation Cleared")

    # Test 2: Insufficient Capital Rejection
    res2 = engine.open_position(ticker="RELIANCE", qty=50, entry_price=2900.0, stop_loss=2800.0, target_price=3100.0)
    # Cost = 145,000 > Available 55,000
    assert res2["success"] is False
    assert "Insufficient capital" in res2["reason"]
    print("[PASS] Test 2 | Capital Limit Safeguard Successfully Blocked Excessive Size")

    # Test 3: Invalid SL / Target Parameters
    res3 = engine.open_position(ticker="INFY", qty=10, entry_price=1500.0, stop_loss=1520.0, target_price=1600.0) # SL > Entry
    assert res3["success"] is False
    assert "Invalid Risk/Reward boundary" in res3["reason"]
    print("[PASS] Test 3 | Inverted Risk/Reward Level Setup Rejected")

    # Test 4: Mark-to-Market Price Updates & Position Liquidation
    engine.update_market_price("TATAMOTORS", 940.0) # +$40 per share gain
    summary_before = engine.get_summary()
    assert summary_before["unrealized_pnl"] == 2000.0 # 50 * 40

    close_res = engine.close_position("TATAMOTORS", exit_price=940.0)
    assert close_res["success"] is True
    assert close_res["realized_pnl"] == 2000.0
    assert engine.available_capital == 102000.0 # 55,000 + 47,000
    print("[PASS] Test 4 | Mark-to-Market Tracking & Realized PnL Accounting Verified")

    print("\nPhase 9B Position State Engine Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase9b_tests()
