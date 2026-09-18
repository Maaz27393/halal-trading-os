import sys
import os

PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from provider_connectors.step2_chartink_scanner import ChartinkScannerConnector

def test_step2_pipeline():
    print("=" * 70)
    print("RUNNING PROVIDER STEP 2: CHARTINK TECHNICAL SCANNER FILTER TEST")
    print("=" * 70)

    assert LIVE_AUTO_EXECUTION is False, "Governance Violation!"
    
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    connector = ChartinkScannerConnector(permission_gateway=perm_gateway, role="analyst_agent")
    assert connector.connect()

    # The canonical Halal universe established in Step 1
    canonical_halal_universe = ["RELIANCE", "TCS"]

    # Sample Chartink scan clause
    sample_scan_clause = "( {cash} ( latest close > latest ema ( latest close , 20 ) and latest volume > 100000 ) )"

    candidates = connector.run_technical_scan_against_universe(canonical_halal_universe, sample_scan_clause)

    # Verify that unapproved technical breakouts (like UNAPPROVED_STOCK) are automatically dropped
    symbols = [c.symbol for c in candidates]
    assert "UNAPPROVED_STOCK" not in symbols, "Security violation: Non-halal stock leaked through technical scan!"
    assert "RELIANCE" in symbols, "Expected halal candidate RELIANCE missing!"
    
    print(f" -> SUCCESS: Technical scan filtered successfully. Approved candidate setups: {symbols}")

    connector.disconnect()
    print("=" * 70)
    print("PROVIDER STEP 2 VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_step2_pipeline()