import sys
import logging
from typing import Dict, Any


VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"
PROVIDER_DIR = rf"{ECOSYSTEM_DIR}\provider_connectors"
SECURITY_DIR = rf"{VAULT_ROOT}\security"

for path in [
    VAULT_ROOT,
    ECOSYSTEM_DIR,
    PROVIDER_DIR,
    SECURITY_DIR,
]:
    if path not in sys.path:
        sys.path.insert(0, path)


from security.gateway import PermissionGateway
from nse_connector import NSEConnector


# ============================================================
# FASTMCP IMPORT
# ============================================================

try:
    from fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        FastMCP = None


logger = logging.getLogger("NSEMCPv1")


if FastMCP is None:
    raise ImportError(
        "FastMCP is not installed. "
        "Please run: pip install fastmcp"
    )


# ============================================================
# SERVER INITIALIZATION
# ============================================================

mcp = FastMCP("NSE Market Data MCP v1")


gateway = PermissionGateway()
connector = NSEConnector(gateway)


# ============================================================
# V1 - MARKET STATUS
# ============================================================

@mcp.tool()
def get_market_status() -> Dict[str, Any]:
    """
    Fetch current NSE exchange market operation status.

    Read-only. No order or execution capability.
    """

    connector._assert_read_only()

    return connector.fetch_market_status()


# ============================================================
# V1 - INDEX VITALS
# ============================================================

@mcp.tool()
def get_index_vitals(index_symbol: str = "NIFTY 50") -> dict:
    """Fetch verified live NSE index vitals."""
    connector._assert_read_only()
    return connector.fetch_index_vitals(index_symbol)

# ============================================================
# V1 - INDIA VIX
# ============================================================

@mcp.tool()
def get_india_vix() -> Dict[str, Any]:
    """
    Fetch live India VIX metrics.

    Read-only. No order or execution capability.
    """

    connector._assert_read_only()

    return connector.fetch_india_vix()


# ============================================================
# V1.1 - CAPITAL MARKET SNAPSHOT
# ============================================================

@mcp.tool()
def get_capital_market_snapshot() -> Dict[str, Any]:
    """
    Retrieve the verified NSE Capital Market snapshot/status
    from the explicitly identified Capital Market segment.

    No fallback to unrelated market segments.
    Read-only. No order or execution capability.
    """

    connector._assert_read_only()

    return connector.fetch_capital_market_snapshot()


# ============================================================
# V1.1 - ADVANCE / DECLINE
# ============================================================

@mcp.tool()
def get_advance_decline() -> Dict[str, Any]:
    """
    Retrieve verified NSE advance/decline breadth statistics.

    Missing fields are not converted to fabricated zero values.
    No unrelated index record is substituted.

    Read-only. No order or execution capability.
    """

    connector._assert_read_only()

    return connector.fetch_advance_decline()


# ============================================================
# SERVER ENTRY POINT
# ============================================================

if __name__ == "__main__":
    mcp.run()