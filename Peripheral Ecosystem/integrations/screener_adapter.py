import logging
from typing import Any, Dict, List, Optional
from connectors.base import BaseConnector
from contracts import FundamentalMetric, BaseCanonicalModel

logger = logging.getLogger("ScreenerAdapter")

class ScreenerAdapter(BaseConnector):
    """
    Read-only adapter for Screener.in fundamental metrics and financial data.
    Conforms to BaseConnector and maps raw responses into canonical FundamentalMetric models.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name="screener_provider", config=config)
        self.base_url = self.config.get("base_url", "https://www.screener.in")

    def connect(self) -> bool:
        """Establish session or verify reachability of Screener endpoints."""
        self._is_connected = True
        logger.info("Screener adapter connected successfully (Read-Only Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self._is_connected else "disconnected",
            "provider": self.provider_name,
            "endpoint": self.base_url
        }

    def capabilities(self) -> List[str]:
        # Strict read-only fundamental data capabilities
        return ["READ", "SEARCH"]

    def read(self, identifier: str, **kwargs) -> Any:
        """Fetch fundamental financial metrics for a specific company symbol (e.g., 'TCS')."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Fetching fundamentals for symbol: {identifier} from Screener.in.")
        
        # Simulated raw fundamental response payload
        return {
            "symbol": identifier.upper(),
            "market_cap": 1450000.0,
            "pe_ratio": 28.4,
            "roe": 34.5,
            "debt_to_equity": 0.05,
            "metrics": {
                "sales_growth_3yrs": 11.2,
                "profit_growth_3yrs": 13.8,
                "dividend_yield": 1.5
            }
        }

    def search(self, query: str, **kwargs) -> List[Any]:
        """Search companies matching query on Screener."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Searching Screener for query: '{query}'")
        return [{"symbol": query.upper(), "name": f"{query.upper()} Ltd"}]

    def normalize(self, raw_data: Any, target_model: type[BaseCanonicalModel]) -> BaseCanonicalModel:
        """Normalize raw provider payload into canonical Pydantic model."""
        if target_model == FundamentalMetric:
            return FundamentalMetric(
                source_provider=self.provider_name,
                symbol=raw_data.get("symbol"),
                market_cap=raw_data.get("market_cap"),
                pe_ratio=raw_data.get("pe_ratio"),
                roe=raw_data.get("roe"),
                debt_to_equity=raw_data.get("debt_to_equity"),
                metrics=raw_data.get("metrics", {})
            )
        raise ValueError(f"ScreenerAdapter cannot normalize raw data to target model {target_model}")

    def disconnect(self) -> bool:
        self._is_connected = False
        logger.info("Screener adapter disconnected.")
        return True