import os
import sys
import json

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"
OPERATIONAL_DIR = rf"{ECOSYSTEM_DIR}\operational_layer"
PROVIDER_DIR = rf"{ECOSYSTEM_DIR}\provider_connectors"

# Ensure all necessary ecosystem directories are in sys.path
for path in [VAULT_ROOT, ECOSYSTEM_DIR, OPERATIONAL_DIR, PROVIDER_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from security.gateway import PermissionGateway
from screener_connector import ScreenerConnector

def run_screener_tests():
    print("=" * 60)
    print("SCREENER.IN INGESTION CONNECTOR - REGRESSION TEST")
    print("=" * 60)

    gateway = PermissionGateway()
    data_cache_dir = rf"{ECOSYSTEM_DIR}\data_cache\screener"
    os.makedirs(data_cache_dir, exist_ok=True)

    connector = ScreenerConnector(gateway, data_root=data_cache_dir)

    # 1. Verify Governance Invariants
    print("\n[1] Verifying Governance Invariants...")
    print(f"   READ_ONLY            : {connector.READ_ONLY}")
    print(f"   LIVE_AUTO_EXECUTION  : {connector.LIVE_AUTO_EXECUTION}")
    print(f"   ORDER_CAPABILITY     : {connector.ORDER_CAPABILITY}")
    print(f"   EXECUTION_AUTHORITY  : {connector.EXECUTION_AUTHORITY}")

    assert connector.READ_ONLY is True
    assert connector.LIVE_AUTO_EXECUTION is False
    assert connector.ORDER_CAPABILITY == "NONE"
    assert connector.EXECUTION_AUTHORITY == "NONE"
    print("   ✅ Governance invariants verified.")

    # 2. Test FAIL_CLOSED Behavior (Missing File)
    print("\n[2] Testing FAIL_CLOSED behavior for missing symbol...")
    fail_res = connector.get_company_fundamentals("NONEXISTENT")
    print(f"   Status : {fail_res.get('status')}")
    print(f"   Error  : {fail_res.get('error')}")
    assert fail_res.get("status") == "FAIL_CLOSED"
    print("   ✅ FAIL_CLOSED verified successfully.")

    # 3. Test Success & Normalization with Local CSV Fixture
    print("\n[3] Creating Local CSV Fixture for 'RELIANCE'...")
    fixture_path = os.path.join(data_cache_dir, "RELIANCE.csv")
    
    csv_content = """Metric,Value
Market Capitalization,1950000
P/E,28.5
ROCE,12.4
ROE,10.2
Debt to Equity,0.35
Sales growth 3Years,11.2
Profit growth 3Years,14.5
OPM,15.8
Net Profit,75000
EPS,120.5
Sales,250000
Profit,22000
Total Assets,1500000
Total Liabilities,600000
Reserves,800000
Borrowings,200000
Cash,50000
"""
    with open(fixture_path, "w", encoding="utf-8-sig") as f:
        f.write(csv_content)
    print(f"   ✅ Fixture written to: {fixture_path}")

    # 4. Test Fundamentals Extraction
    print("\n[4] Testing get_company_fundamentals...")
    fund_res = connector.get_company_fundamentals("RELIANCE")
    print(f"   Status : {fund_res.get('status')}")
    print(f"   Data   : {json.dumps(fund_res.get('data'), indent=2)}")
    assert fund_res.get("status") == "SUCCESS"
    assert fund_res.get("data", {}).get("pe") == "28.5"

    # 5. Test Financial Summary Extraction
    print("\n[5] Testing get_financial_summary...")
    fin_res = connector.get_financial_summary("RELIANCE")
    print(f"   Status : {fin_res.get('status')}")
    print(f"   Data   : {json.dumps(fin_res.get('data'), indent=2)}")
    assert fin_res.get("status") == "SUCCESS"

    print("\n" + "=" * 60)
    print("SCREENER REGRESSION TESTS COMPLETED SUCCESSFULLY ✅")
    print("=" * 60)

if __name__ == "__main__":
    run_screener_tests()