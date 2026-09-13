import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from connectors.broker_base import LIVE_AUTO_EXECUTION
from security.live_gate import LiveExecutionGate, LiveGateViolationError

def run_activation_gate_verification():
    print("Initializing P3.10 - Controlled Activation Gate Verification...")

    # 1. Verify immutable default core rule
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: Default execution state must be False!"
    print("Governance Check Passed: System defaults securely to paper/shadow mode.")

    # 2. Verify protocol file existence
    protocol_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "governance", "activation_gate_protocol.md")
    )
    assert os.path.exists(protocol_path), "Governance Error: Activation Gate Protocol document is missing!"
    print(f"Activation Gate Protocol Document Verified at: {protocol_path}")

    # 3. Confirm live execution remains locked without multi-factor authorization
    os.environ["TRADING_ENV"] = "SANDBOX"
    try:
        LiveExecutionGate.assert_live_authorization("ANY_TOKEN", "PRODUCTION")
        raise AssertionError("Security Breach: Live activation allowed under sandbox conditions!")
    except LiveGateViolationError:
        print("Activation Gate Verified: Unauthorized live activation attempts are correctly rejected.")

    print("P3.10 Controlled Activation Gate & Governance Framework Verified Successfully!")

if __name__ == "__main__":
    run_activation_gate_verification()