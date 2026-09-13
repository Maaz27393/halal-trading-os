import logging
import time
from typing import Any, Dict, List, Optional
from registry.models import ProviderRegistration

logger = logging.getLogger("CapabilityResolver")

class CapabilityResolver:
    """
    Registry and routing engine supporting priority-based fallback providers 
    and health checks across capability namespaces.
    """

    def __init__(self):
        # Maps namespace string to a list of ProviderRegistration sorted by priority
        self._providers: Dict[str, List[ProviderRegistration]] = {}

    def register_provider(self, registration: ProviderRegistration) -> None:
        """Register a provider adapter under a specific capability namespace."""
        if registration.namespace not in self._providers:
            self._providers[registration.namespace] = []
        
        self._providers[registration.namespace].append(registration)
        # Sort by priority (lowest number = highest priority)
        self._providers[registration.namespace].sort(key=lambda p: p.priority)
        logger.info(f"Registered provider '{registration.provider_id}' for namespace '{registration.namespace}' with priority {registration.priority}.")

    def resolve_adapter(self, namespace: str) -> Any:
        """Retrieve the highest-priority healthy adapter instance for the given namespace."""
        registrations = self._providers.get(namespace)
        if not registrations:
            raise ValueError(f"No providers registered for namespace '{namespace}'.")
        
        for reg in registrations:
            try:
                health_status = reg.adapter_instance.health()
                if health_status.get("status") == "healthy":
                    return reg.adapter_instance
            except Exception as e:
                logger.warning(f"Provider '{reg.provider_id}' health check failed: {e}")

        # Fallback to top priority even if health check is questionable, or raise error
        return registrations[0].adapter_instance

    def execute_via_capability(self, namespace: str, method_name: str, required_operation: str, *args, **kwargs) -> Any:
        """Execute a method with automatic fallback across registered providers in the namespace."""
        registrations = self._providers.get(namespace)
        if not registrations:
            raise ValueError(f"No providers registered for namespace '{namespace}'.")

        last_exception = None
        for reg in registrations:
            adapter = reg.adapter_instance
            try:
                # Verify capabilities
                if required_operation not in adapter.capabilities():
                    continue

                method = getattr(adapter, method_name, None)
                if not method or not callable(method):
                    continue

                logger.info(f"Attempting execution via provider '{reg.provider_id}' on namespace '{namespace}'.")
                result = method(*args, **kwargs)
                return result
            except Exception as e:
                last_exception = e
                logger.warning(f"Provider '{reg.provider_id}' failed execution. Trying next fallback... Error: {e}")

        raise RuntimeError(f"All providers for namespace '{namespace}' failed execution. Last error: {last_exception}")