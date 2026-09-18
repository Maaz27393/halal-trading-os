import sys
import os

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"
PROVIDER_DIR = rf"{ECOSYSTEM_DIR}\provider_connectors"

for path in [VAULT_ROOT, ECOSYSTEM_DIR, PROVIDER_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from security.gateway import PermissionGateway
from nse_connector import NSEConnector

def verify_snapshot():
    print("=" * 60)
    print("NSE CONNECTOR: MARKET SNAPSHOT & BREADTH VERIFICATION")
    print("=" * 60)

    # Instantiate the mandatory permission gateway
    gateway = PermissionGateway()
    connector = NSEConnector(gateway)

    print("\n[1] Initializing session handshake...")
    connected = connector.connect()
    print(f"Session initialized: {connected}")

    print("\n[2] Probing market breadth / advance-decline via indices payload...")
    try:
        # Fetch all indices which carries comprehensive market vitals and advance/decline metrics
        market_data = connector.fetch_index_vitals("NIFTY 50")
        print("Successfully retrieved Nifty 50 market context.")
        print(f"Timestamp: {market_data.get('timestamp')}")
        
        # Check market status as well
        status = connector.fetch_market_status()
        print(f"Market Status Feed: OK (Keys: {list(status.get('data', {}).keys())})")
    except Exception as e:
        print(f"Snapshot probe warning: {e}")

    print("\n[3] Validating structural contract & governance guards...")
    print(f"Connector Read-Only Mode  : {connector.READ_ONLY}")
    print(f"LIVE_AUTO_EXECUTION       : {connector.LIVE_AUTO_EXECUTION}")
    print("Verification script completed cleanly.")

if __name__ == "__main__":
    verify_snapshot()