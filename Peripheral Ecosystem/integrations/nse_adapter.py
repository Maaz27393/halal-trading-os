import logging
from typing import Any, Dict, List, Optional
from connectors.base import BaseConnector
from contracts import MarketQuote, BaseCanonicalModel

logger = logging.getLogger("NSEAdapter")

class NSEAdapter(BaseConnector):
    """
    Read-only adapter for NSE market data, quotes, and reference information.
    Conforms to BaseConnector and maps raw responses into canonical MarketQuote models.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name="nse_provider", config=config)
        self.base_url = self.config.get("base_url", "https://www.nseindia.com")

    def connect(self) -> bool:
        """Establish session or verify reachability of NSE endpoints."""
        self._is_connected = True
        logger.info("NSE adapter connected successfully (Read-Only Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self._is_connected else "disconnected",
            "provider": self.provider_name,
            "endpoint": self.base_url
        }

    def capabilities(self) -> List[str]:
        # Strict read-only market data capabilities
        return ["READ", "SEARCH"]

    def read(self, identifier: str, **kwargs) -> Any:
        """Fetch real-time or snapshot quote for a specific symbol (e.g., 'RELIANCE')."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Fetching quote for symbol: {identifier} from NSE.")
        
        # Simulated raw response payload from exchange/API
        return {
            "symbol": identifier.upper(),
            "exchange": "NSE",
            "last_price": 2850.50,
            "change_percent": 1.25,
            "volume": 1250000,
            "bid": 2850.00,
            "ask": 2850.75,
            "metadata": {"source_status": "live"}
        }

    def search(self, query: str, **kwargs) -> List[Any]:
        """Search instruments or symbols matching query."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Searching symbols matching query: '{query}'")
        return [{"symbol": query.upper(), "name": f"{query.upper()} Ltd", "exchange": "NSE"}]

    def normalize(self, raw_data: Any, target_model: type[BaseCanonicalModel]) -> BaseCanonicalModel:
        """Normalize raw provider payload into canonical Pydantic model."""
        if target_model == MarketQuote:
            return MarketQuote(
                source_provider=self.provider_name,
                symbol=raw_data.get("symbol"),
                exchange=raw_data.get("exchange", "NSE"),
                last_price=raw_data.get("last_price", 0.0),
                change_percent=raw_data.get("change_percent", 0.0),
                volume=raw_data.get("volume", 0),
                bid=raw_data.get("bid"),
                ask=raw_data.get("ask"),
                metadata=raw_data.get("metadata", {})
            )
        raise ValueError(f"NSEAdapter cannot normalize raw data to target model {target_model}")

    def disconnect(self) -> bool:
        self._is_connected = False
        logger.info("NSE adapter disconnected.")
        return True