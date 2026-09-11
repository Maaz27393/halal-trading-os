import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from execution_safety_interlock import ExecutionSafetyInterlock

def run_phase11b_tests():
    print("=== STARTING PHASE 11B: EXECUTION SAFETY INTERLOCK TESTS ===")
    interlock = ExecutionSafetyInterlock(max_trade_value=50000.0, max_daily_loss=10000.0, max_price_deviation_pct=3.0)

    valid_payload = {
        "trading_symbol": "TATAMOTORS-EQ",
        "quantity": 40,
        "price": 1000.0
    }

    # Test 1: Standard Compliant Order Approval
    res1 = interlock.validate_order(valid_payload, ltp=1000.0, is_halal=True, current_daily_loss=0.0)
    assert res1["approved"] is True
    assert res1["reason"] == "PASSED_ALL_RISK_GUARDS"
    print("[PASS] Test 1 | Standard Compliant Order Approval Verified")

    # Test 2: Emergency Kill-Switch & Non-Halal Block
    interlock.trigger_kill_switch(True)
    res_kill = interlock.validate_order(valid_payload, ltp=1000.0, is_halal=True)
    assert res_kill["approved"] is False
    assert res_kill["reason"] == "KILL_SWITCH_ACTIVE"

    interlock.trigger_kill_switch(False) # Reset
    res_halal = interlock.validate_order(valid_payload, ltp=1000.0, is_halal=False)
    assert res_halal["approved"] is False
    assert res_halal["reason"] == "NON_HALAL_ASSET_REJECTED"
    print("[PASS] Test 2 | Kill-Switch & Shariah Compliance Rejections Verified")

    # Test 3: Capital Cap, Daily Loss, & Fat-Finger Interceptions
    oversized_payload = {"quantity": 100, "price": 1000.0} # Value = 100,000 > 50,000 limit
    res_cap = interlock.validate_order(oversized_payload, ltp=1000.0, is_halal=True)
    assert res_cap["approved"] is False
    assert "EXCEEDS_MAX_TRADE_VALUE" in res_cap["reason"]

    res_loss = interlock.validate_order(valid_payload, ltp=1000.0, is_halal=True, current_daily_loss=10500.0)
    assert res_loss["approved"] is False
    assert "DAILY_LOSS_LIMIT_BREACHED" in res_loss["reason"]

    fat_finger_payload = {"quantity": 40, "price": 1100.0} # 10% above LTP 1000.0
    res_fat = interlock.validate_order(fat_finger_payload, ltp=1000.0, is_halal=True)
    assert res_fat["approved"] is False
    assert "FAT_FINGER_PRICE_DEVIATION" in res_fat["reason"]
    print("[PASS] Test 3 | Max Value, Daily Loss, and Fat-Finger Limits Verified")

    print("\nPhase 11B Execution Safety Interlock Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase11b_tests()
