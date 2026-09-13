import logging
from typing import Any, Dict, List, Optional
from connectors.base import BaseConnector
from contracts import MacroIndicator, BaseCanonicalModel

logger = logging.getLogger("MacroAdapter")

class MacroAdapter(BaseConnector):
    """
    Read-only adapter for macroeconomic indicators (interest rates, CPI inflation, GDP).
    Conforms to BaseConnector and maps raw metrics into canonical MacroIndicator models.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name="macro_provider", config=config)
        self.endpoint = self.config.get("endpoint", "https://api.macro-economic.local")

    def connect(self) -> bool:
        """Establish session or verify reachability of macro data feeds."""
        self._is_connected = True
        logger.info("Macro adapter connected successfully (Read-Only Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self._is_connected else "disconnected",
            "provider": self.provider_name,
            "endpoint": self.endpoint
        }

    def capabilities(self) -> List[str]:
        # Strict read-only macroeconomic capabilities
        return ["READ", "SEARCH"]

    def read(self, identifier: str, **kwargs) -> Any:
        """Fetch macroeconomic indicator data for a specific metric (e.g., 'REPO_RATE' or 'CPI_INFLATION')."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Fetching macro indicator for: {identifier}")
        
        # Simulated raw macroeconomic payload
        return {
            "indicator_name": identifier.upper(),
            "value": 6.5,
            "unit": "%",
            "period": "Q3 2026",
            "country": "India"
        }

    def search(self, query: str, **kwargs) -> List[Any]:
        """Search available macroeconomic indicators matching query keywords."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Searching macro indicators for query: '{query}'")
        return [{"indicator_id": "macro_01", "name": f"Macro Metric for {query.upper()}"}]

    def normalize(self, raw_data: Any, target_model: type[BaseCanonicalModel]) -> BaseCanonicalModel:
        """Normalize raw provider payload into canonical Pydantic model."""
        if target_model == MacroIndicator:
            return MacroIndicator(
                source_provider=self.provider_name,
                indicator_name=raw_data.get("indicator_name", "UNKNOWN"),
                value=raw_data.get("value", 0.0),
                unit=raw_data.get("unit", "%"),
                period=raw_data.get("period", "Current"),
                country=raw_data.get("country", "India")
            )
        raise ValueError(f"MacroAdapter cannot normalize raw data to target model {target_model}")

    def disconnect(self) -> bool:
        self._is_connected = False
        logger.info("Macro adapter disconnected.")
        return True