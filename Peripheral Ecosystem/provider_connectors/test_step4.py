import sys
import os

PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from provider_connectors.step3_kite_readonly import ReadOnlyKiteConnector, TradeJournalRecord
from provider_connectors.step4_excel_journal_sync import ExcelJournalSyncConnector

def test_step4_pipeline():
    print("=" * 70)
    print("RUNNING PROVIDER STEP 4: EXCEL JOURNAL & POWER BI SYNC TEST")
    print("=" * 70)

    assert LIVE_AUTO_EXECUTION is False, "Governance Violation!"
    
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    # 1. Pull trades from Read-Only Kite connector (Step 3)
    kite_connector = ReadOnlyKiteConnector(permission_gateway=perm_gateway, role="analyst_agent")
    assert kite_connector.connect()
    trades = kite_connector.get_executed_trades_for_journal()
    kite_connector.disconnect()

    # 2. Sync trades to Excel Journal (Step 4)
    sync_connector = ExcelJournalSyncConnector(permission_gateway=perm_gateway, role="analyst_agent")
    assert sync_connector.connect()
    
    journal_path = sync_connector.sync_trades_to_journal(trades)
    sync_connector.disconnect()

    assert os.path.exists(journal_path), "Journal export file not found on disk!"
    
    print(f" -> SUCCESS: Trades successfully synced to Power BI-ready journal: {journal_path}")

    print("=" * 70)
    print("PROVIDER STEP 4 & FULL PIPELINE VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_step4_pipeline()