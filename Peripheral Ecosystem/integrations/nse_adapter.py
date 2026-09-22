import sys
import logging
from typing import Any, Dict, List, Optional

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if VAULT_ROOT not in sys.path:
    sys.path.insert(0, VAULT_ROOT)

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from connectors.base import BaseConnector
from contracts import MarketQuote, BaseCanonicalModel
from security.gateway import PermissionGateway
from provider_connectors.nse_connector import NSEConnector

logger = logging.getLogger("NSEAdapter")

class NSEAdapter(BaseConnector):
    """
    Read-only adapter for NSE market data, quotes, and reference information.
    Bridges BaseConnector interface to the real live NSEConnector backend.
    Conforms strictly to read-only governance and canonical MarketQuote models.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name="nse_provider", config=config)
        self.base_url = self.config.get("base_url", "https://www.nseindia.com")
        
        # Initialize the security gateway and real NSE connector
        self.gateway = PermissionGateway()
        self.nse_connector = NSEConnector(permission_gateway=self.gateway)

    def connect(self) -> bool:
        """Establish session or verify reachability of NSE endpoints via real connector."""
        success = self.nse_connector.connect()
        self._is_connected = success
        if success:
            logger.info("NSE adapter connected successfully to live NSE backend (Read-Only Mode).")
        else:
            logger.warning("NSE adapter handshake returned non-ok status, operating in degraded mode.")
        return self._is_connected

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self._is_connected else "disconnected",
            "provider": self.provider_name,
            "endpoint": self.base_url,
            "read_only": self.nse_connector.READ_ONLY
        }

    def capabilities(self) -> List[str]:
        # Strict read-only market data capabilities
        return ["READ", "SEARCH", "MARKET_STATUS", "INDEX_VITALS", "EQUITY_QUOTE"]

    def read(self, identifier: str, **kwargs) -> Any:
        """Fetch live snapshot quote for a specific equity symbol (e.g., 'RELIANCE') from NSE."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Fetching live quote for symbol: {identifier} from NSE.")
        
        # Delegate to the real NSEConnector
        result = self.nse_connector.fetch_equity(identifier)
        return result

    def search(self, query: str, **kwargs) -> List[Any]:
        """Search instruments or symbols matching query using index/market vitals."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Searching symbols matching query: '{query}'")
        
        # Fallback search wrapper using index vitals or direct equity fetch attempt
        equity_result = self.nse_connector.fetch_equity(query)
        if equity_result.get("status") == "OK":
            return [equity_result]
        return [{"symbol": query.upper(), "name": f"{query.upper()} Ltd", "exchange": "NSE", "status": "UNAVAILABLE"}]

    def normalize(self, raw_data: Any, target_model: type[BaseCanonicalModel]) -> BaseCanonicalModel:
        """Normalize raw provider payload into canonical Pydantic model."""
        if target_model == MarketQuote:
            # Handle real NSE payload structure vs fallback mock structure
            data = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            price_info = data.get("priceInfo", {})
            
            # Extract fields with safe fallbacks
            last_price = price_info.get("lastPrice") or data.get("last_price", 0.0)
            change_pct = price_info.get("pChange") or data.get("change_percent", 0.0)
            volume = price_info.get("totalTradedVolume") or data.get("volume", 0)
            bid = price_info.get("buyPrice1") or data.get("bid")
            ask = price_info.get("sellPrice1") or data.get("ask")
            
            symbol = (
                data.get("info", {}).get("symbol") 
                or raw_data.get("symbol") 
                or "UNKNOWN"
            )

            return MarketQuote(
                source_provider=self.provider_name,
                symbol=str(symbol).upper(),
                exchange=raw_data.get("exchange", "NSE"),
                last_price=float(last_price) if last_price else 0.0,
                change_percent=float(change_pct) if change_pct else 0.0,
                volume=int(volume) if volume else 0,
                bid=float(bid) if bid else None,
                ask=float(ask) if ask else None,
                metadata={
                    "source_status": raw_data.get("status", "UNKNOWN"),
                    "provenance": raw_data.get("source", "LIVE_NSE_PUBLIC_REST")
                }
            )
            
        raise ValueError(f"NSEAdapter cannot normalize raw data to target model {target_model}")

    def disconnect(self) -> bool:
        self._is_connected = False
        logger.info("NSE adapter disconnected.")
        return True
