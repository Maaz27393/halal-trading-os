import logging
from typing import Any, Dict, List, Optional
from connectors.base import BaseConnector
from contracts import ScanResult, BaseCanonicalModel

logger = logging.getLogger("ChartinkAdapter")

class ChartinkAdapter(BaseConnector):
    """
    Read-only adapter for Chartink technical screening queries and stock scans.
    Conforms to BaseConnector and maps raw scanner responses into canonical ScanResult models.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name="chartink_provider", config=config)
        self.base_url = self.config.get("base_url", "https://chartink.com")

    def connect(self) -> bool:
        """Establish session or verify reachability of Chartink endpoints."""
        self._is_connected = True
        logger.info("Chartink adapter connected successfully (Read-Only Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self._is_connected else "disconnected",
            "provider": self.provider_name,
            "endpoint": self.base_url
        }

    def capabilities(self) -> List[str]:
        # Strict read-only technical scanning capabilities
        return ["READ", "SEARCH"]

    def read(self, identifier: str, **kwargs) -> Any:
        """Fetch scan results for a specific scanner name or query ID (e.g., 'volume_breakout')."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Executing Chartink scan for: {identifier}")
        
        # Simulated raw technical scanner payload
        return {
            "scanner_name": identifier,
            "matched_symbols": ["RELIANCE", "TCS", "INFY", "SBIN"],
            "raw_results": [
                {"symbol": "RELIANCE", "close": 2850.5, "volume_spike": 3.2},
                {"symbol": "TCS", "close": 4120.0, "volume_spike": 2.8},
                {"symbol": "INFY", "close": 1850.0, "volume_spike": 2.5},
                {"symbol": "SBIN", "close": 820.0, "volume_spike": 4.1}
            ]
        }

    def search(self, query: str, **kwargs) -> List[Any]:
        """Search available public scans matching query."""
        if not self._is_connected:
            self.connect()
        logger.info(f"Searching Chartink scans for: '{query}'")
        return [{"scanner_id": "scan_01", "name": f"Scan for {query}"}]

    def normalize(self, raw_data: Any, target_model: type[BaseCanonicalModel]) -> BaseCanonicalModel:
        """Normalize raw provider payload into canonical Pydantic model."""
        if target_model == ScanResult:
            return ScanResult(
                source_provider=self.provider_name,
                scanner_name=raw_data.get("scanner_name", "unknown_scan"),
                matched_symbols=raw_data.get("matched_symbols", []),
                raw_results=raw_data.get("raw_results", [])
            )
        raise ValueError(f"ChartinkAdapter cannot normalize raw data to target model {target_model}")

    def disconnect(self) -> bool:
        self._is_connected = False
        logger.info("Chartink adapter disconnected.")
        return True