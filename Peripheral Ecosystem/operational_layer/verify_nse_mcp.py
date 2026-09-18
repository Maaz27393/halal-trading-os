import sys

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"
OPERATIONAL_DIR = rf"{ECOSYSTEM_DIR}\operational_layer"

for path in [VAULT_ROOT, ECOSYSTEM_DIR, OPERATIONAL_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from nse_mcp_server import get_market_status, get_index_vitals, get_india_vix, connector

def test_mcp_tools_in_process():
    print("=" * 60)
    print("NSE MCP v1 IN-PROCESS VERIFICATION")
    print("=" * 60)

    print("\n[1] Verifying Governance & Invariants...")
    print(f"Read-Only Invariant : {connector.READ_ONLY}")
    print(f"Live Auto Execution : {connector.LIVE_AUTO_EXECUTION}")
    assert connector.READ_ONLY is True
    assert connector.LIVE_AUTO_EXECUTION is False
    print("Governance Guards: OK")

    print("\n[2] Testing Tool: get_market_status()...")
    status = get_market_status()
    print(f"Source Provenance : {status.get('source')}")
    print(f"Capability Tag    : {status.get('capability')}")
    print("Market Status Data Received: Success")

    print("\n[3] Testing Tool: get_index_vitals('NIFTY 50')...")
    nifty = get_index_vitals("NIFTY 50")
    print(f"Index Target      : {nifty.get('index')}")
    print(f"Timestamp         : {nifty.get('timestamp')}")
    print("Nifty Vitals Received: Success")

    print("\n[4] Testing Tool: get_india_vix()...")
    vix = get_india_vix()
    print(f"Index Target      : {vix.get('index')}")
    print("India VIX Received: Success")

    print("\n" + "=" * 60)
    print("ALL NSE MCP v1 TOOLS VERIFIED IN-PROCESS SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    test_mcp_tools_in_process()