import sys
import os

# Point Python path to Peripheral Ecosystem root
PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p7_expansion.agentic_refinement import ResearchDraft
from track_a_workspace.docs_exporter.doc_adapter import A2DocumentExporter

def run_a_2_tests():
    print("=" * 70)
    print("STARTING TRACK A.2 — GOOGLE DOCS / WORD EXPORTER VERIFICATION TESTS")
    print("=" * 70)

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and exporter
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    exporter = A2DocumentExporter(permission_gateway=perm_gateway, role="analyst_agent")
    assert exporter.connect(), "Connection failed for A2DocumentExporter!"
    print(" -> SUCCESS: Exporter established secure session with WRITE permission.")

    # 3. Test health and capabilities
    health = exporter.health()
    assert health["status"] == "HEALTHY", "Health check failed!"
    caps = exporter.capabilities()
    assert "export_to_vault" in caps, "Capabilities mismatch!"
    print(f" -> SUCCESS: Health check passed. Capabilities declared: {len(caps)}")

    # 4. Create sample research draft and export
    sample_draft = ResearchDraft(
        title="Track A.2 Integration Test Report",
        content="This is a verified test document generated via the secure A.2 document export connector.",
        provenance_sources=["Gmail Ingestion Source: msg_001", "P7 Agent Pipeline"],
        author_agent="A2_Test_Agent",
        has_execution_payload=False
    )

    exported_item = exporter.export_draft(sample_draft)
    assert os.path.exists(exported_item.target_path), "Exported file not found on disk!"
    print(f" -> SUCCESS: Document successfully exported to: {exported_item.target_path}")

    # 5. Test unauthorized access block
    unauth_gateway = PermissionGateway() # No WRITE permissions granted
    unauth_exporter = A2DocumentExporter(permission_gateway=unauth_gateway, role="unauthorized_role")
    try:
        unauth_exporter.connect()
        raise AssertionError("SECURITY FAILURE: Unauthorized role bypassed permission check!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized document export connection successfully blocked: {e}")

    exporter.disconnect()
    print("=" * 70)
    print("TRACK A.2 DOCUMENT EXPORTER VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_a_2_tests()