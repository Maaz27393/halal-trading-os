import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.live_gate import LiveExecutionGate, LiveGateViolationError
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_live_gate_tests():
    print("Initializing P3.8 - Live Execution Gating & Safety Enforcement Tests...")

    # 1. Verify default immutable state remains strictly False
    assert LIVE_AUTO_EXECUTION is False, "Safety Violation: LIVE_AUTO_EXECUTION must remain False by default!"
    print("Default Guardrail Verified: LIVE_AUTO_EXECUTION = False")

    # 2. Test unauthorized access attempt (Default/incorrect token and sandbox environment)
    os.environ["TRADING_ENV"] = "SANDBOX"
    try:
        LiveExecutionGate.assert_live_authorization(override_token="INVALID_TOKEN", environment_flag="PRODUCTION")
        raise AssertionError("Security Failure: Live gate unlocked with invalid credentials!")
    except LiveGateViolationError as e:
        print(f"Live Gate Successfully Blocked Unauthorized Attempt: {e}")

    # 3. Test authorized simulation (Demonstrating the gating check function without bypassing system guardrail)
    os.environ["TRADING_ENV"] = "PRODUCTION"
    os.environ["HALAL_LIVE_OVERRIDE_TOKEN"] = "SECURE_ADMIN_TOKEN_9988"
    
    try:
        authorized = LiveExecutionGate.assert_live_authorization(
            override_token="SECURE_ADMIN_TOKEN_9988",
            environment_flag="PRODUCTION"
        )
        assert authorized is True
        print("Live Gate Multi-Factor Check Passed (Execution remains safely offline by default core rule).")
    finally:
        # Clean up environment variables
        os.environ["TRADING_ENV"] = "SANDBOX"
        os.environ["HALAL_LIVE_OVERRIDE_TOKEN"] = "FROZEN_SECURE_DEFAULT_TOKEN"

    print("P3.8 Live Execution Gating & Safety Enforcement Tests Passed Successfully!")

if __name__ == "__main__":
    run_live_gate_tests()