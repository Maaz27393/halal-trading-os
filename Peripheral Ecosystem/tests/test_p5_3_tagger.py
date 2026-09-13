import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p5_expansion.vault_tagger import VaultCrossReferencingEngine
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_p5_3_test():
    print("Initializing P5.3 - Vault Cross-Referencing & Tagging Engine Verification...")

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and vault target
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    engine = VaultCrossReferencingEngine(permission_gateway=perm_gateway, vault_base_path=vault_base)

    # 3. Execute tagging engine workflow
    audit_path = engine.process_and_tag_vault(caller_role="analyst_agent")

    print(f"Audit Report Path: {audit_path}")
    assert os.path.exists(audit_path), "Export Error: Vault audit markdown file was not created!"

    with open(audit_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Vault Cross-Referencing & Tagging Audit" in content

    print("P5.3 Vault Cross-Referencing & Tagging Engine Verified Successfully!")

if __name__ == "__main__":
    run_p5_3_test()