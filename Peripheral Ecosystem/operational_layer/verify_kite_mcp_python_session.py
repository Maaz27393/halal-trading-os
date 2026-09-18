import re
import sys
import webbrowser

sys.path.insert(
    0,
    r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\provider_connectors",
)

from step3_kite_mcp_connector import KiteMCPReadOnlyConnector
from security.gateway import PermissionGateway


def extract_login_url(message: str) -> str:
    match = re.search(
        r"https://mcp\.kite\.trade/authorize\?session_id=[^\s\)]+",
        message,
    )

    if not match:
        return ""

    return match.group(0)


def main() -> None:
    connector = KiteMCPReadOnlyConnector(
        PermissionGateway()
    )

    try:
        print("=" * 70)
        print("HALAL TRADING OS - KITE MCP PERSISTENT SESSION LOGIN TEST")
        print("=" * 70)

        connector.connect()

        print("\nExposed tools:")
        for tool in sorted(connector._tool_names):
            print(f"   {tool}")

        print("\nStarting Kite login...")

        login_result = connector.login()

        print("\nLogin result:")
        print(login_result)

        if login_result.get("status") != "SUCCESS":
            raise RuntimeError(
                "Kite login tool did not return SUCCESS."
            )

        message = (
            login_result
            .get("data", {})
            .get("message", "")
        )

        login_url = extract_login_url(message)

        if login_url:
            print("\nOpening Kite authorization page...")
            print(login_url)
            webbrowser.open(login_url)

        print(
            "\nComplete the Zerodha login and 2FA in the browser."
        )

        input(
            "\nAfter authorization is complete, "
            "press ENTER in this PowerShell window..."
        )

        print(
            "\nTesting LTP using the SAME persistent MCP session..."
        )

        result = connector.ltp(
            ["NSE:INFY"]
        )

        print("\nLTP result:")
        print(result)

        if result.get("status") == "SUCCESS":
            print("\nKITE MCP PERSISTENT SESSION TEST: PASS")
        else:
            print("\nKITE MCP PERSISTENT SESSION TEST: FAIL")

    finally:
        connector.close()
        print("\nMCP session closed.")


if __name__ == "__main__":
    main()