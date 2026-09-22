import sys
import os
import logging
from typing import Dict, Any

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from security.gateway import PermissionGateway
from registry.resolver import CapabilityResolver
from registry.models import ProviderRegistration
from integrations.nse_adapter import NSEAdapter
from contracts import MarketQuote

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NSEMCPv1")

# Initialize P2 Architecture Components
gateway = PermissionGateway()
resolver = CapabilityResolver()
nse_adapter = NSEAdapter(config={"gateway": gateway})

resolver.register_provider(ProviderRegistration(
    provider_id="nse_live",
    namespace="market.quotes",
    adapter_instance=nse_adapter,
    priority=10
))

if FastMCP:
    mcp = FastMCP("HalalTradingOS-NSE-P2")

    @mcp.tool()
    def get_nse_quote(symbol: str) -> dict:
        """Fetch canonical market quote for a given NSE symbol via CapabilityResolver."""
        try:
            raw_quote = resolver.execute_via_capability(
                namespace="market.quotes",
                method_name="read",
                required_operation="READ",
                identifier=symbol
            )
            canonical_quote = nse_adapter.normalize(raw_quote, MarketQuote)
            return canonical_quote.model_dump()
        except Exception as e:
            logger.error(f"Failed to fetch quote for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol.upper()}

    @mcp.tool()
    def search_nse_symbols(query: str) -> list:
        """Search NSE symbols via P2 adapter."""
        try:
            return nse_adapter.search(query)
        except Exception as e:
            logger.error(f"Search failed for {query}: {e}")
            return []

if __name__ == "__main__":
    if FastMCP:
        logger.info("Starting NSE MCP Server (P2 Architecture Mode)...")
        mcp.run()
    else:
        logger.error("FastMCP library not found. Please install fastmcp to run the MCP server.")
