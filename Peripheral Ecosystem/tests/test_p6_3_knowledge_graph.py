import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p6_expansion.knowledge_graph import ObsidianKnowledgeGraphSynthesizer
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_p6_3_test():
    print("Initializing P6.3 - Obsidian Knowledge Graph Synthesizer Verification...")

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and vault target
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    synthesizer = ObsidianKnowledgeGraphSynthesizer(permission_gateway=perm_gateway, vault_base_path=vault_base)

    # 3. Execute graph synthesis workflow
    exported_path = synthesizer.synthesize_and_export_graph(caller_role="analyst_agent")

    print(f"Exported Knowledge Graph Artifact Path: {exported_path}")
    assert os.path.exists(exported_path), "Export Error: Knowledge graph markdown file was not created!"

    with open(exported_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Energy Sector Breakout" in content
        assert "Semantic Clusters" in content

    print("P6.3 Obsidian Knowledge Graph Synthesizer Verified Successfully!")

if __name__ == "__main__":
    run_p6_3_test()