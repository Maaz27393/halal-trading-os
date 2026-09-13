import sys
import logging
from typing import Any, Callable, Dict, List, Optional
from permissions.gateway import PermissionGateway, PermissionViolationError

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (PeripheralMCP) %(message)s"
)
logger = logging.getLogger("PeripheralMCP")

class LocalMCPServer:
    """
    Lightweight local MCP Server framework for the Peripheral Ecosystem.
    Manages a secure tool registry, integrates the PermissionGateway, 
    and dispatches calls safely without touching the frozen trading core.
    """

    def __init__(self, permission_gateway: Optional[PermissionGateway] = None):
        self.registry: Dict[str, Dict[str, Any]] = {}
        self.gateway = permission_gateway or PermissionGateway(strict_mode=True)
        logger.info("LocalMCPServer initialized with active PermissionGateway.")

    def register_tool(
        self, 
        name: str, 
        func: Callable[..., Any], 
        description: str, 
        required_capability: str = "READ"
    ) -> None:
        """Register an isolated tool with a mandatory capability tag."""
        if name in self.registry:
            logger.warning(f"Overwriting existing tool registration: '{name}'")
            
        self.registry[name] = {
            "function": func,
            "description": description,
            "required_capability": required_capability.upper()
        }
        logger.info(f"Registered tool '{name}' requiring capability '{required_capability.upper()}'.")

    def health(self) -> Dict[str, Any]:
        """Return server status and registered tool count."""
        return {
            "status": "healthy",
            "registered_tools_count": len(self.registry),
            "tools": list(self.registry.keys()),
            "firewall_active": True
        }

    def dispatch(self, tool_name: str, **kwargs: Any) -> Any:
        """
        Dispatches a tool call after checking the permission gateway.
        Hard-blocks any unregistered or unauthorized actions.
        """
        if tool_name not in self.registry:
            raise KeyError(f"MCP Error: Tool '{tool_name}' is not registered in the local server.")

        tool_meta = self.registry[tool_name]
        required_capability = tool_meta["required_capability"]
        func = tool_meta["function"]

        # Security check via Permission Gateway (simulating a virtual connector context or direct policy check)
        logger.info(f"Dispatching tool '{tool_name}' under capability check '{required_capability}'.")
        
        if required_capability in self.gateway.blocked_capabilities:
            raise PermissionViolationError(
                f"FIREWALL BLOCK: Tool '{tool_name}' requires blocked capability '{required_capability}'."
            )

        try:
            result = func(**kwargs)
            logger.info(f"Tool '{tool_name}' executed successfully.")
            return result
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {str(e)}")
            raise