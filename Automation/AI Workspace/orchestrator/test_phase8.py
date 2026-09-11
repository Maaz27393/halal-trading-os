import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from execution_state_machine import ExecutionOrder, OrderState

def run_phase8_tests():
    print("=== STARTING PHASE 8: EXECUTION STATE MACHINE TESTS ===")

    # Test 1: Complete Lifecycle (CREATED -> PRECHECK -> SUBMITTED -> FILLED)
    order1 = ExecutionOrder(order_id="ORD_001", ticker="TATAMOTORS", side="BUY", qty=100, limit_price=980.0)
    assert order1.state == OrderState.CREATED

    order1.pass_precheck("SOP execution passed")
    assert order1.state == OrderState.PRECHECK_PASSED

    order1.submit_to_broker("BROKER_REF_9912")
    assert order1.state == OrderState.SUBMITTED

    success = order1.execute_fill(execution_price=981.0, qty=100) # 0.1% slippage < 0.5%
    assert success is True
    assert order1.state == OrderState.FILLED
    assert order1.filled_qty == 100
    print("[PASS] Test 1 | Clean Order Lifecycle Transitions Cleared")

    # Test 2: Slippage Breach Causes Order Rejection
    order2 = ExecutionOrder(order_id="ORD_002", ticker="INFY", side="BUY", qty=50, limit_price=1500.0, max_slippage_pct=0.5)
    order2.pass_precheck()
    order2.submit_to_broker("BROKER_REF_9913")
    
    # Fill at 1515.0 represents a 1.0% slippage (exceeds 0.5% limit)
    success2 = order2.execute_fill(execution_price=1515.0, qty=50)
    assert success2 is False
    assert order2.state == OrderState.REJECTED
    print("[PASS] Test 2 | Excessive Slippage Execution Protection Triggered")

    # Test 3: Invalid State Transition Safeguard
    order3 = ExecutionOrder(order_id="ORD_003", ticker="TCS", side="BUY", qty=20, limit_price=4000.0)
    try:
        order3.submit_to_broker("BROKER_REF_INVALID") # Skipping PRECHECK_PASSED state
        assert False, "Should have raised ValueError"
    except ValueError:
        print("[PASS] Test 3 | Out-of-Sequence State Transition Blocked")

    # Test 4: Order Cancellation Lifecycle
    order4 = ExecutionOrder(order_id="ORD_004", ticker="RELIANCE", side="BUY", qty=30, limit_price=2900.0)
    order4.pass_precheck()
    order4.cancel("User cancelled prior to broker submission")
    assert order4.state == OrderState.CANCELLED
    print("[PASS] Test 4 | Order Cancellation Handling Verified")

    print("\nPhase 8 Execution State Machine Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase8_tests()
