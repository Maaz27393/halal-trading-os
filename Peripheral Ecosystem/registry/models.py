from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

@dataclass
class ProviderRegistration:
    """Metadata and handles for a registered provider adapter."""
    provider_id: str
    namespace: str  # e.g., 'market.quotes', 'fundamental.metrics', 'llm.completion'
    adapter_instance: Any
    priority: int = 10  # Lower number = higher priority
    enabled: bool = True
    health_status: str = "healthy"
    supported_operations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)