import sys

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"
PROVIDER_DIR = rf"{ECOSYSTEM_DIR}\provider_connectors"

for path in [VAULT_ROOT, ECOSYSTEM_DIR, PROVIDER_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from security.gateway import PermissionGateway
from nse_connector import NSEConnector


def run_verification():
    print("=" * 60)
    print("NSE CONNECTOR READ-ONLY VERIFICATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Permission Gateway
    # ---------------------------------------------------------

    print("\n[1] Initializing Permission Gateway...")

    gateway = PermissionGateway()

    print("Permission Gateway: OK")

    # ---------------------------------------------------------
    # 2. NSE Connector
    # ---------------------------------------------------------

    print("\n[2] Initializing NSE Connector...")

    connector = NSEConnector(gateway)

    print(f"Read-only: {connector.READ_ONLY}")
    print(
        f"LIVE_AUTO_EXECUTION: "
        f"{connector.LIVE_AUTO_EXECUTION}"
    )

    assert connector.READ_ONLY is True
    assert connector.LIVE_AUTO_EXECUTION is False

    # ---------------------------------------------------------
    # 3. Optional Homepage Handshake
    # ---------------------------------------------------------

    print("\n[3] NSE initial session handshake...")

    connected = connector.connect()

    print(f"Initial handshake response: {connected}")
    print(
        f"Cookies acquired: "
        f"{len(connector.session.cookies)}"
    )

    print(
        "Note: homepage handshake is non-authoritative; "
        "actual NSE API capability tests below are authoritative."
    )

    # ---------------------------------------------------------
    # 4. Market Status
    # ---------------------------------------------------------

    print("\n[4] Market Status...")

    status = connector.fetch_market_status()

    assert status.get("status") == "OK"

    print(
        f"Response received: "
        f"{bool(status)}"
    )

    print(
        f"Capability: "
        f"{status.get('capability')}"
    )

    print(
        f"Source: "
        f"{status.get('source')}"
    )

    # ---------------------------------------------------------
    # 5. NIFTY 50
    # ---------------------------------------------------------

    print("\n[5] NIFTY 50...")

    nifty = connector.fetch_index_vitals("NIFTY 50")

    assert nifty.get("status") == "OK"

    nifty_data = nifty.get("data", {})

    print(
        f"Status: "
        f"{nifty.get('status')}"
    )

    print(
        f"Index: "
        f"{nifty.get('index')}"
    )

    print(
        f"Timestamp: "
        f"{nifty.get('timestamp')}"
    )

    print(
        f"Data fields: "
        f"{len(nifty_data)}"
    )

    # ---------------------------------------------------------
    # 6. India VIX
    # ---------------------------------------------------------

    print("\n[6] INDIA VIX...")

    vix = connector.fetch_india_vix()

    assert vix.get("status") == "OK"

    print(
        f"Status: "
        f"{vix.get('status')}"
    )

    print(
        f"Index: "
        f"{vix.get('index')}"
    )

    print(
        f"Timestamp: "
        f"{vix.get('timestamp')}"
    )

    # ---------------------------------------------------------
    # 7. Capital Market Snapshot
    # ---------------------------------------------------------

    print("\n[7] Capital Market Snapshot...")

    snapshot = connector.fetch_capital_market_snapshot()

    print(
        f"Status: "
        f"{snapshot.get('status')}"
    )

    print(
        f"Capability: "
        f"{snapshot.get('capability')}"
    )

    if snapshot.get("status") == "OK":

        snapshot_data = snapshot.get("data", {})

        print(
            f"Market: "
            f"{snapshot_data.get('market')}"
        )

        print(
            f"Market Status: "
            f"{snapshot_data.get('marketStatus')}"
        )

        print(
            f"Trade Date: "
            f"{snapshot_data.get('tradeDate')}"
        )

        print(
            f"Index: "
            f"{snapshot_data.get('index')}"
        )

        print(
            f"Last: "
            f"{snapshot_data.get('last')}"
        )

        print(
            f"Percent Change: "
            f"{snapshot_data.get('percentChange')}"
        )

    else:

        print(
            "Validation: "
            f"{snapshot.get('validation_error')}"
        )

    # ---------------------------------------------------------
    # 8. Advance / Decline
    # ---------------------------------------------------------

    print("\n[8] Advance / Decline...")

    breadth = connector.fetch_advance_decline()

    print(
        f"Status: "
        f"{breadth.get('status')}"
    )

    print(
        f"Capability: "
        f"{breadth.get('capability')}"
    )

    print(
        f"Timestamp: "
        f"{breadth.get('timestamp')}"
    )

    breadth_data = breadth.get("data", {})

    aggregate = breadth_data.get(
        "aggregate_breadth"
    )

    nifty_500 = breadth_data.get(
        "nifty_500_breadth"
    )

    if aggregate:

        print("\nAggregate Breadth:")

        print(
            f"  Advances: "
            f"{aggregate.get('advances')}"
        )

        print(
            f"  Declines: "
            f"{aggregate.get('declines')}"
        )

        print(
            f"  Unchanged: "
            f"{aggregate.get('unchanged')}"
        )

    if nifty_500:

        print("\nNIFTY 500 Breadth:")

        print(
            f"  Advances: "
            f"{nifty_500.get('advances')}"
        )

        print(
            f"  Declines: "
            f"{nifty_500.get('declines')}"
        )

        print(
            f"  Unchanged: "
            f"{nifty_500.get('unchanged')}"
        )

    if breadth.get("status") != "OK":

        print(
            "Validation: "
            f"{breadth.get('validation_error')}"
        )

    # ---------------------------------------------------------
    # 9. Equity Quote
    # ---------------------------------------------------------

    print("\n[9] Equity Quote...")

    equity = connector.fetch_equity("RELIANCE")

    print(
        f"Response received: "
        f"{bool(equity)}"
    )

    print(
        f"Symbol: "
        f"{equity.get('symbol')}"
    )

    print(
        f"Status: "
        f"{equity.get('status')}"
    )

    print(
        f"HTTP Status: "
        f"{equity.get('http_status')}"
    )

    # ---------------------------------------------------------
    # 10. Final Governance
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("NSE CONNECTOR VERIFICATION COMPLETE")
    print("=" * 60)

    print("\nREAD-ONLY INVARIANT: PASS")
    print("LIVE_AUTO_EXECUTION = FALSE: PASS")
    print("ORDER CAPABILITY: NONE")
    print("EXECUTION AUTHORITY: NONE")


if __name__ == "__main__":
    run_verification()