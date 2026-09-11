import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from broker_session_manager import BrokerSessionManager
from failure_stress_harness import FailureStressHarness

def run_phase12b_tests():
    print("=== STARTING PHASE 12B: FAILURE INJECTION & RESILIENCE STRESS TESTS ===")
    
    harness = FailureStressHarness(max_allowed_slippage_pct=0.5)
    broker = BrokerSessionManager(broker_name="Shoonya")
    broker.authenticate("MOCK_KEY", "USER123", "123456")

    # Test 1: Network Timeout Interception & Reconciliation Guard
    order_payload = {"trading_symbol": "RELIANCE-EQ", "quantity": 10, "price": 2500.0}
    timeout_res = harness.process_order_with_timeout_guard(order_payload, simulate_timeout=True)
    assert timeout_res["success"] is False
    assert timeout_res["status"] == "TIMEOUT_INTERCEPTED"
    assert timeout_res["action"] == "CANCEL_AND_RECONCILE"
    print("[PASS] Test 1 | Network Timeout & State Reconciliation Interception Verified")

    # Test 2: Pre-Dispatch Token Expiry Safeguard
    token_res = harness.validate_session_before_dispatch(broker, simulate_token_expiry=True)
    assert token_res["dispatch_allowed"] is False
    assert token_res["reason"] == "TOKEN_EXPIRED_MID_EXECUTION"
    assert token_res["action"] == "TRIGGER_AUTO_REAUTH_OR_HALT"
    print("[PASS] Test 2 | Pre-Dispatch Mid-Execution Token Expiry Guard Verified")

    # Test 3: Post-Signal Slippage Surge Interception
    # Scenario A: Normal Drift (0.2%)
    slip_ok = harness.check_post_signal_slippage(expected_price=1000.0, current_market_price=1002.0)
    assert slip_ok["allowed"] is True

    # Scenario B: Excessive Slippage Surge (1.2% > 0.5% max limit)
    slip_fail = harness.check_post_signal_slippage(expected_price=1000.0, current_market_price=1012.0)
    assert slip_fail["allowed"] is False
    assert slip_fail["action"] == "ABORT_ORDER_SUBMISSION"
    assert "SLIPPAGE_SURGE_EXCEEDED" in slip_fail["reason"]
    print("[PASS] Test 3 | Post-Signal Price Drift & Slippage Protection Verified")

    # Test 4: Broker Rejection Error Handling & Clean State Transitions
    rejection1 = harness.handle_broker_rejection("ORD_991", "INSUFFICIENT_MARGIN")
    assert rejection1["status"] == "REJECTED_BY_BROKER"
    assert rejection1["system_action"] == "HALT_STRATEGY_CHECK_CAPITAL"

    rejection2 = harness.handle_broker_rejection("ORD_992", "CIRCUIT_LIMIT_REACHED")
    assert rejection2["system_action"] == "CANCEL_ORDER_MARK_UNSERVICEABLE"
    print("[PASS] Test 4 | Broker Error Codes & State Recovery Matrix Verified")

    print("\nPhase 12B Failure Injection & Resilience Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase12b_tests()
