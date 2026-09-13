import sys
import os

# Point Python path to Peripheral Ecosystem root
PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from track_a_workspace.sheets_connector.sheets_adapter import A3SheetsExcelConnector

def run_a_3_tests():
    print("=" * 70)
    print("STARTING TRACK A.3 — GOOGLE SHEETS / EXCEL CONNECTOR VERIFICATION TESTS")
    print("=" * 70)

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and connector
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    connector = A3SheetsExcelConnector(permission_gateway=perm_gateway, role="analyst_agent")
    assert connector.connect(), "Connection failed for A3SheetsExcelConnector!"
    print(" -> SUCCESS: Connector established secure session with READ/WRITE permissions.")

    # 3. Test health and capabilities
    health = connector.health()
    assert health["status"] == "HEALTHY", "Health check failed!"
    caps = connector.capabilities()
    assert "read_tabular_dataset" in caps and "export_tabular_dataset" in caps, "Capabilities mismatch!"
    print(f" -> SUCCESS: Health check passed. Capabilities declared: {len(caps)}")

    # 4. Test reading tabular dataset
    rows = connector.read_sheet("Backtest_Performance_Summary")
    assert len(rows) > 0, "Tabular ingestion returned zero rows!"
    print(f" -> SUCCESS: Ingested {len(rows)} structured performance row(s).")

    # 5. Test exporting tabular dataset
    export_data = [r.data for r in rows]
    target_csv = connector.export_sheet("Strategy_Metrics", export_data)
    assert os.path.exists(target_csv), "Exported CSV file not found on disk!"
    print(f" -> SUCCESS: Tabular dataset successfully exported to: {target_csv}")

    # 6. Test unauthorized access block
    unauth_gateway = PermissionGateway()
    unauth_connector = A3SheetsExcelConnector(permission_gateway=unauth_gateway, role="unauthorized_role")
    try:
        unauth_connector.connect()
        raise AssertionError("SECURITY FAILURE: Unauthorized role bypassed permission check!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized tabular connection successfully blocked: {e}")

    connector.disconnect()
    print("=" * 70)
    print("TRACK A.3 SHEETS/EXCEL CONNECTOR VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_a_3_tests()