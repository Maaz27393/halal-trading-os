from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from contracts import BaseCanonicalModel

class BaseConnector(ABC):
    """
    Abstract Base Class for all external peripheral connectors.
    Enforces a uniform interface regardless of underlying provider (API, scraper, webhook, etc.).
    """
    
    def __init__(self, provider_name: str, config: Optional[Dict[str, Any]] = None):
        self.provider_name = provider_name
        self.config = config or {}
        self._is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection or session with the external provider."""
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Return operational health status and connectivity check of the provider."""
        pass

    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return supported operation types (e.g., ['READ', 'SEARCH'])."""
        pass

    @abstractmethod
    def read(self, identifier: str, **kwargs) -> Any:
        """Fetch raw record or data item by identifier."""
        pass

    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Any]:
        """Perform a search operation against the provider."""
        pass

    @abstractmethod
    def normalize(self, raw_data: Any, target_model: type[BaseCanonicalModel]) -> BaseCanonicalModel:
        """Transform raw provider-specific payload into a standardized canonical Pydantic model."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Safely tear down connection or session."""
        pass