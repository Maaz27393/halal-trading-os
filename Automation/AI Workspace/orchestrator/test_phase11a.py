import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from broker_session_manager import BrokerSessionManager

def run_phase11a_tests():
    print("=== STARTING PHASE 11A: BROKER SESSION MANAGER TESTS ===")
    manager = BrokerSessionManager(broker_name="Shoonya", token_expiry_seconds=3600)

    # Test 1: Authentication & Token Generation
    auth_res = manager.authenticate("MOCK_API_KEY", "USER123", "654321")
    assert auth_res["status"] == "SUCCESS"
    assert manager.is_session_valid() is True
    print("[PASS] Test 1 | Broker TOTP Session Authentication Verified")

    # Test 2: Standardized Live Order Payload Formatting
    order_payload = manager.format_live_order_payload(
        ticker="TATAMOTORS-EQ",
        side="BUY",
        qty=50,
        order_type="LIMIT",
        price=1012.50
    )
    assert order_payload["broker"] == "Shoonya"
    assert order_payload["trading_symbol"] == "TATAMOTORS-EQ"
    assert order_payload["quantity"] == 50
    assert order_payload["price"] == 1012.50
    print("[PASS] Test 2 | Standardized Order Payload Formatting Verified")

    # Test 3: Expired/Invalid Session Rejection
    manager.active_session["expires_at"] = int(time.time()) - 10 # Force expire
    assert manager.is_session_valid() is False

    try:
        manager.format_live_order_payload("TATAMOTORS-EQ", "BUY", 50)
        assert False, "Should have raised PermissionError"
    except PermissionError:
        print("[PASS] Test 3 | Expired Session Execution Interception Verified")

    print("\nPhase 11A Broker Session Manager Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase11a_tests()
