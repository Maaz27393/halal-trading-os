import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from execution_safety_interlock import ExecutionSafetyInterlock
from broker_session_manager import BrokerSessionManager
from live_order_router import LiveOrderRouter

def run_phase11c_tests():
    print("=== STARTING PHASE 11C: LIVE ORDER ROUTER TESTS ===")
    interlock = ExecutionSafetyInterlock(max_trade_value=50000.0, max_daily_loss=10000.0)
    broker = BrokerSessionManager(broker_name="Shoonya")
    broker.authenticate("MOCK_KEY", "USER123", "123456")

    router = LiveOrderRouter(interlock, broker)

    order_req = {
        "trading_symbol": "TATAMOTORS-EQ",
        "transaction_type": "BUY",
        "quantity": 30,
        "price_type": "LIMIT",
        "price": 1000.0
    }

    # Test 1: Route & Submit Order via Interlock Guard
    submit_res = router.route_and_submit_order(order_req, ltp=1000.0, is_halal=True)
    assert submit_res["status"] == "SUBMITTED"
    assert submit_res["order_id"] is not None
    order_id = submit_res["order_id"]
    print("[PASS] Test 1 | Live Order Routing & Pre-Trade Interlock Integration Verified")

    # Test 2: Lifecycle State Machine Transitions
    state1 = router.update_order_state(order_id, "PENDING")
    assert state1["state"] == "PENDING"

    state2 = router.update_order_state(order_id, "PARTIALLY_FILLED", filled_qty=15, fill_price=1000.0)
    assert state2["state"] == "PARTIALLY_FILLED"
    assert state2["filled_qty"] == 15

    state3 = router.update_order_state(order_id, "PARTIALLY_FILLED", filled_qty=30, fill_price=1000.0)
    assert state3["state"] == "FILLED"
    assert state3["filled_qty"] == 30
    print("[PASS] Test 3 | Lifecycle State Transitions & Full Fill Resolution Verified")

    # Test 3: Unfilled Execution Timeout Cancellation
    order_req_timeout = {
        "trading_symbol": "INFY-EQ",
        "transaction_type": "BUY",
        "quantity": 10,
        "price_type": "LIMIT",
        "price": 1500.0
    }
    submit_timeout = router.route_and_submit_order(order_req_timeout, ltp=1500.0, is_halal=True)
    timeout_order_id = submit_timeout["order_id"]

    # Force simulated aging
    router.orders[timeout_order_id]["updated_at"] = int(time.time()) - 40
    timeout_res = router.handle_execution_timeout(timeout_order_id, max_age_seconds=30)
    assert timeout_res["action"] == "CANCELLED_DUE_TO_TIMEOUT"
    assert router.orders[timeout_order_id]["state"] == "CANCELLED"
    print("[PASS] Test 3 | Unfilled Execution Timeout & Cancellation Guard Verified")

    print("\nPhase 11C Live Order Router Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase11c_tests()
