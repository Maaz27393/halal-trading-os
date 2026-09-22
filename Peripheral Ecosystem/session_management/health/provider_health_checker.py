import logging
from typing import Dict, Any, Optional
from session_management.managers.session_manager import SessionManager
from session_management.contracts.session_contract import SessionMetadata

logger = logging.getLogger("ProviderHealthChecker")

class ProviderHealthChecker:
    """
    Bridges existing P2 adapter health methods with the SessionManager 
    to evaluate operational status without trading authority.
    """
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def evaluate_adapter(self, provider_id: str, adapter_instance: Any) -> SessionMetadata:
        """
        Queries an adapter's standard .health() method and updates 
        the session state accordingly using the fail-closed model.
        """
        try:
            if hasattr(adapter_instance, "health") and callable(adapter_instance.health):
                health_data = adapter_instance.health()
            else:
                health_data = {"status": "error", "reason": "No health method available"}

            status = health_data.get("status", "disconnected")
            is_healthy = status in ["connected", "healthy", "ok"]
            reason = health_data.get("reason") or health_data.get("error")

            return self.session_manager.update_session_status(
                provider_id=provider_id,
                success=is_healthy,
                failure_reason=reason,
                raw_health=health_data
            )
        except Exception as e:
            logger.exception(f"Exception during health check for provider '{provider_id}': {e}")
            return self.session_manager.update_session_status(
                provider_id=provider_id,
                success=False,
                failure_reason=str(e)
            )
