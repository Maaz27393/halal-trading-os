import sys
import os

PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from provider_connectors.step1_fundamental_halal import FundamentalHalalIngestionConnector

def test_step1_pipeline():
    print("=" * 70)
    print("RUNNING PROVIDER STEP 1: SCREENER.IN + MUSAFFA HALAL FILTER TEST")
    print("=" * 70)

    assert LIVE_AUTO_EXECUTION is False, "Governance Violation!"
    
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    connector = FundamentalHalalIngestionConnector(permission_gateway=perm_gateway, role="analyst_agent")
    assert connector.connect()

    # Mock raw Screener.in dump (simulating 300 stocks downloaded)
    raw_screener_dump = [
        {"symbol": "RELIANCE", "company_name": "Reliance Industries", "sector": "Energy", "market_cap_cr": 1800000, "roe": 15.5, "debt_to_equity": 0.35},
        {"symbol": "TCS", "company_name": "Tata Consultancy Services", "sector": "IT", "market_cap_cr": 1400000, "roe": 45.2, "debt_to_equity": 0.02},
        {"symbol": "CONVENTIONAL_BANK_X", "company_name": "Bank X", "sector": "Financials", "market_cap_cr": 50000, "roe": 14.0, "debt_to_equity": 4.5}, # Non-halal debt/business
    ]

    # Mock Musaffa approved Shariah compliance symbols list
    musaffa_halal_symbols = ["RELIANCE", "TCS"] 

    halal_universe = connector.ingest_screener_and_filter_halal(raw_screener_dump, musaffa_halal_symbols)

    assert len(halal_universe) == 2, f"Expected 2 halal-verified stocks, got {len(halal_universe)}"
    assert halal_universe[0].symbol == "RELIANCE"
    assert halal_universe[1].symbol == "TCS"
    print(f" -> SUCCESS: Canonical Halal Universe established with {len(halal_universe)} approved symbols.")

    connector.disconnect()
    print("=" * 70)
    print("PROVIDER STEP 1 VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_step1_pipeline()