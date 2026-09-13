from typing import Any, List, Optional
from connectors.base import BaseConnector

class PermissionViolationError(PermissionError):
    """Raised when an agent or workflow attempts an unauthorized operation or blocked capability."""
    pass

class PermissionGateway:
    """
    Enforces security and capability boundaries between the peripheral agent 
    and external connectors. Hard-blocks L4 execution actions.
    """
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        # Hard-blocked capabilities for the current phase (L4 Execution Firewall)
        self.blocked_capabilities = {"EXECUTE", "DELETE"}

    def validate_action(self, connector: BaseConnector, action: str, **kwargs: Any) -> bool:
        """
        Validates whether a connector is permitted to perform a specific action.
        Raises PermissionViolationError if the action is blocked or unsupported.
        """
        action = action.upper()

        # 1. Check against the global hard-blocked capabilities
        if action in self.blocked_capabilities:
            raise PermissionViolationError(
                f"FIREWALL BLOCK: Action '{action}' on provider '{connector.provider_name}' "
                f"is strictly prohibited by the L4 execution firewall."
            )

        # 2. Check if the connector officially supports the requested capability
        supported_capabilities = [c.upper() for c in connector.capabilities()]
        if action not in supported_capabilities:
            if self.strict_mode:
                raise PermissionViolationError(
                    f"CAPABILITY DENIED: Provider '{connector.provider_name}' does not support "
                    f"or declare capability '{action}'. Supported: {supported_capabilities}"
                )
            return False

        return True

    def execute_guarded(self, connector: BaseConnector, action: str, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Guards a connector method execution by validating permissions first.
        """
        self.validate_action(connector, action, **kwargs)
        
        if not hasattr(connector, method_name):
            raise AttributeError(f"Connector '{connector.provider_name}' has no method '{method_name}'.")
        
        method = getattr(connector, method_name)
        return method(*args, **kwargs)