import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p7_expansion.adaptive_triggers import EventTriggerObserver

def run_p7_2_tests():
    print("=" * 70)
    print("STARTING P7.2 — EVENT-DRIVEN ADAPTIVE TRIGGERS VERIFICATION")
    print("=" * 70)

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and observer
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    observer = EventTriggerObserver(permission_gateway=perm_gateway, vault_base_path=vault_base)

    # 3. Simulate incoming macro variance event
    print("\n[TEST-01] Simulating MACRO_VARIANCE_ALERT event trigger...")
    macro_payload = {"indicator": "USD/INR & Bond Yield Spike", "details": "Volatility shift detected in alternative macro feed."}
    artifact_path = observer.process_incoming_event(
        event_type="MACRO_VARIANCE_ALERT",
        event_payload=macro_payload,
        caller_role="analyst_agent"
    )

    assert os.path.exists(artifact_path), "Trigger Error: Refined research artifact not generated from macro event!"
    print(f" -> SUCCESS: Macro event successfully processed and refined at {artifact_path}")

    # 4. Simulate scheduled research pulse event
    print("\n[TEST-02] Simulating SCHEDULED_RESEARCH_PULSE event trigger...")
    pulse_artifact_path = observer.process_incoming_event(
        event_type="SCHEDULED_RESEARCH_PULSE",
        event_payload={},
        caller_role="analyst_agent"
    )

    assert os.path.exists(pulse_artifact_path), "Trigger Error: Refined research artifact not generated from scheduled pulse!"
    print(f" -> SUCCESS: Scheduled pulse successfully processed and refined at {pulse_artifact_path}")

    print("=" * 70)
    print("P7.2 EVENT-DRIVEN ADAPTIVE TRIGGERS VERIFIED SUCCESSFULLY!")
    print("READY FOR P7.3 TRANSITION.")
    print("=" * 70)

if __name__ == "__main__":
    run_p7_2_tests()