import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from execution_state_machine import ExecutionOrder, OrderState
from position_state_engine import PositionStateEngine
from failure_recovery_engine import FailureRecoveryEngine

def run_phase9f_tests():
    print("=== STARTING PHASE 9F: FAILURE RECOVERY TESTS ===")
    recovery_engine = FailureRecoveryEngine(stale_timeout_seconds=10.0)
    pos_engine = PositionStateEngine(initial_capital=100000.0)

    # Test 1: Stale Submitted Order Auto-Cancellation
    now = time.time()
    stale_order = ExecutionOrder(order_id="REC_001", ticker="TATAMOTORS", side="BUY", qty=50, limit_price=980.0)
    stale_order.pass_precheck()
    stale_order.submit_to_broker("BROKER_1")
    stale_order.created_at = now - 15.0 # 15s old > 10s limit

    log1 = recovery_engine.process_stale_orders([stale_order], current_time=now)
    assert len(log1) == 1
    assert log1[0]["action"] == "AUTO_CANCELLED"
    assert stale_order.state == OrderState.CANCELLED
    print("[PASS] Test 1 | Stale Order Timeout Auto-Cancellation Verified")

    # Test 2: Partial Fill Residual Cancellation
    partial_order = ExecutionOrder(order_id="REC_002", ticker="INFY", side="BUY", qty=100, limit_price=1500.0)
    partial_order.pass_precheck()
    partial_order.submit_to_broker("BROKER_2")
    partial_order.execute_fill(execution_price=1500.0, qty=40)
    partial_order.created_at = now - 12.0 # 12s old

    log2 = recovery_engine.process_stale_orders([partial_order], current_time=now)
    assert len(log2) == 1
    assert log2[0]["action"] == "PARTIAL_RESIDUAL_CANCELLED"
    assert log2[0]["retained_filled_qty"] == 40
    assert partial_order.state == OrderState.CANCELLED
    print("[PASS] Test 2 | Partial Fill Timeout Residual Purge Verified")

    # Test 3: Unexpected Broker Rejection & Ghost Position Cleanup
    rejected_order = ExecutionOrder(order_id="REC_003", ticker="RELIANCE", side="BUY", qty=20, limit_price=2900.0)
    rejected_order.pass_precheck()
    rejected_order.submit_to_broker("BROKER_3")

    # Simulate anomalous ghost entry creation
    pos_engine.positions["RELIANCE"] = "GHOST_ENTRY"

    res3 = recovery_engine.handle_unexpected_rejection(rejected_order, pos_engine, "Exchange Risk Margin Call")
    assert res3["rejection_handled"] is True
    assert res3["ghost_position_purged"] is True
    assert "RELIANCE" not in pos_engine.positions
    assert rejected_order.state == OrderState.REJECTED
    print("[PASS] Test 3 | Broker Rejection & Ghost Position Purge Verified")

    # Test 4: Active Normal Order Left Unmodified
    fresh_order = ExecutionOrder(order_id="REC_004", ticker="TCS", side="BUY", qty=10, limit_price=4000.0)
    fresh_order.pass_precheck()
    fresh_order.submit_to_broker("BROKER_4")
    fresh_order.created_at = now - 2.0 # Only 2s old

    log4 = recovery_engine.process_stale_orders([fresh_order], current_time=now)
    assert len(log4) == 0
    assert fresh_order.state == OrderState.SUBMITTED
    print("[PASS] Test 4 | Active Order Lifecycle Integrity Preserved")

    print("\nPhase 9F Failure Recovery Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase9f_tests()
