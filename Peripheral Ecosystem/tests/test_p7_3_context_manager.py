import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p7_expansion.context_manager import ContextPromptManager

def run_p7_3_tests():
    print("=" * 70)
    print("STARTING P7.3 — CONTEXT & PROMPT ABSTRACTION MANAGER VERIFICATION")
    print("=" * 70)

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and context manager
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    manager = ContextPromptManager(permission_gateway=perm_gateway, vault_base_path=vault_base)

    # 3. Test context packet preparation
    print("\n[TEST-01] Preparing sanitized context packet for cross-vault query...")
    sample_notes = [
        "Sector Correlation Report P6.1 (Nifty IT outperforming)",
        "Risk Modeler P6.2 (EMA Pullback EV = 0.38)"
    ]
    packet = manager.prepare_context_packet(
        topic="Cross-Vault Multi-Timeframe Strategy Evaluation",
        raw_context_notes=sample_notes,
        caller_role="analyst_agent"
    )

    assert packet.guardrail_status is False, "Security Error: Guardrail status in packet is incorrect!"
    assert "ANALYTICAL CONTEXT PACKET" in packet.abstracted_prompt, "Formatting Error: Prompt packet missing required structure!"
    print(f" -> SUCCESS: Context packet successfully structured with token budget: {packet.token_budget_allocated}")

    # 4. Test permission denial
    print("\n[TEST-02] Testing unauthorized context access...")
    try:
        manager.prepare_context_packet(
            topic="Unauthorized Query",
            raw_context_notes=["Confidential Data"],
            caller_role="unauthorized_role"
        )
        raise AssertionError("SECURITY FAILURE: Unauthorized role bypassed READ permission check!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized context access successfully blocked: {e}")

    print("=" * 70)
    print("P7.3 CONTEXT & PROMPT ABSTRACTION MANAGER VERIFIED SUCCESSFULLY!")
    print("READY FOR P7.4 REGRESSION AUDIT & PHASE 7 LOCK.")
    print("=" * 70)

if __name__ == "__main__":
    run_p7_3_tests()