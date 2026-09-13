import sys
import os

# Point Python path to Peripheral Ecosystem root
PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from track_a_workspace.gmail_connector.gmail_adapter import A1GmailConnector
from track_a_workspace.gmail_connector.gmail_normalizer import GmailIngestionNormalizer

def run_a_1_tests():
    print("=" * 70)
    print("STARTING TRACK A.1 — GMAIL CONNECTOR VERIFICATION TESTS")
    print("=" * 70)

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and connector
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    connector = A1GmailConnector(permission_gateway=perm_gateway)
    assert connector.connect(), "Connection failed for A1GmailConnector!"
    print(" -> SUCCESS: Connector established secure read-only session.")

    # 3. Test health and capabilities
    health = connector.health()
    assert health["status"] == "HEALTHY", "Health check failed!"
    caps = connector.capabilities()
    assert "search_emails" in caps and "read_email_body" in caps, "Capabilities mismatch!"
    print(f" -> SUCCESS: Health check passed. Capabilities declared: {len(caps)}")

    # 4. Test secure read & search
    emails = connector.read({"query": "Earnings", "max_results": 5})
    assert len(emails) > 0, "Email ingestion returned zero results for query!"
    print(f" -> SUCCESS: Ingested {len(emails)} filtered email item(s).")

    # 5. Test normalisation into research draft
    draft = GmailIngestionNormalizer.normalize_to_research_draft(emails[0])
    assert "Earnings Alert" in draft.title, "Normalization title mismatch!"
    assert draft.has_execution_payload is False, "Execution safety invariant violated!"
    print(f" -> SUCCESS: Email successfully normalized into research draft: '{draft.title}'")

    # 6. Test unauthorized access block
    unauth_gateway = PermissionGateway()
    unauth_connector = A1GmailConnector(permission_gateway=unauth_gateway, role="unauthorized_role")
    try:
        unauth_connector.connect()
        raise AssertionError("SECURITY FAILURE: Unauthorized role bypassed permission check!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized Gmail connection successfully blocked: {e}")

    connector.disconnect()
    print("=" * 70)
    print("TRACK A.1 GMAIL CONNECTOR VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_a_1_tests()