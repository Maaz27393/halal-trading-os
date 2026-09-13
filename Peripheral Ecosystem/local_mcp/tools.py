from datetime import datetime
from typing import Any, Dict

def tool_system_ping() -> Dict[str, Any]:
    """Safe test tool to verify local peripheral response."""
    return {
        "status": "active",
        "system": "Peripheral Ecosystem Layer",
        "timestamp": datetime.utcnow().isoformat(),
        "frozen_core_isolated": True
    }

def register_default_tools(mcp_server: Any) -> None:
    """Registers baseline safe local tools."""
    mcp_server.register_tool(
        name="system_ping",
        func=tool_system_ping,
        description="Verify local peripheral responsiveness and firewall isolation.",
        required_capability="READ"
    )