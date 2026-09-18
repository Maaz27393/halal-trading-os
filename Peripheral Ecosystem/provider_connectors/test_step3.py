import sys
import os

PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from provider_connectors.step3_kite_readonly import ReadOnlyKiteConnector

def test_step3_pipeline():
    print("=" * 70)
    print("RUNNING PROVIDER STEP 3: KITE READ-ONLY API & JOURNAL SYNC TEST")
    print("=" * 70)

    assert LIVE_AUTO_EXECUTION is False, "Governance Violation!"
    
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    connector = ReadOnlyKiteConnector(permission_gateway=perm_gateway, role="analyst_agent")
    assert connector.connect()

    trades = connector.get_executed_trades_for_journal()

    assert len(trades) > 0, "No trades retrieved for journaling!"
    assert trades[0].has_execution_payload is False, "Safety violation: Execution payload detected!"
    
    print(f" -> SUCCESS: Retrieved {len(trades)} executed trades for automated Excel journaling.")
    for t in trades:
        print(f"    [Trade] {t.trade_id} | {t.transaction_type} {t.quantity} {t.symbol} @ {t.average_price}")

    connector.disconnect()
    print("=" * 70)
    print("PROVIDER STEP 3 VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_step3_pipeline()