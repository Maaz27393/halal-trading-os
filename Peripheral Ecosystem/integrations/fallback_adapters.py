import logging
from typing import Any, Dict, List, Optional
from connectors.base import BaseConnector
from contracts import MarketQuote, BaseCanonicalModel

logger = logging.getLogger("FallbackAdapters")

class FaultyNSEAdapter(BaseConnector):
    """Simulates a primary NSE adapter that experiences downtime/errors."""
    def __init__(self):
        super().__init__(provider_name="faulty_nse_provider")

    def connect(self) -> bool: 
        return True

    def health(self) -> Dict[str, Any]: 
        return {"status": "unhealthy", "provider": self.provider_name}

    def capabilities(self) -> List[str]: 
        return ["READ", "SEARCH"]

    def read(self, identifier: str, **kwargs) -> Any:
        raise ConnectionError("Primary NSE Provider Timeout / Outage!")

    def search(self, query: str, **kwargs) -> List[Any]:
        raise ConnectionError("Primary NSE Provider Timeout / Outage during search!")

    def normalize(self, raw_data: Any, target_model: type[BaseCanonicalModel]) -> BaseCanonicalModel:
        raise NotImplementedError()

    def disconnect(self) -> bool: 
        return True


class BackupNSEAdapter(BaseConnector):
    """Reliable secondary fallback NSE adapter."""
    def __init__(self):
        super().__init__(provider_name="backup_nse_provider")

    def connect(self) -> bool: 
        return True

    def health(self) -> Dict[str, Any]: 
        return {"status": "healthy", "provider": self.provider_name}

    def capabilities(self) -> List[str]: 
        return ["READ", "SEARCH"]

    def read(self, identifier: str, **kwargs) -> Any:
        logger.info("Serving market quote from Backup NSE Provider.")
        return {
            "symbol": identifier.upper(),
            "exchange": "NSE-BACKUP",
            "last_price": 2852.0,
            "change_percent": 1.3,
            "volume": 1200000
        }

    def search(self, query: str, **kwargs) -> List[Any]:
        return [{"symbol": query.upper(), "exchange": "NSE-BACKUP"}]

    def normalize(self, raw_data: Any, target_model: type[BaseCanonicalModel]) -> BaseCanonicalModel:
        if target_model == MarketQuote:
            return MarketQuote(
                source_provider=self.provider_name,
                symbol=raw_data.get("symbol"),
                exchange=raw_data.get("exchange", "NSE"),
                last_price=raw_data.get("last_price", 0.0),
                change_percent=raw_data.get("change_percent", 0.0),
                volume=raw_data.get("volume", 0)
            )
        raise ValueError(f"Cannot normalize to {target_model}")

    def disconnect(self) -> bool: 
        return True