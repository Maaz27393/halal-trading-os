import sys
import os

# Ensure package root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from local_mcp.server import LocalMCPServer
from local_mcp.tools import register_default_tools
from permissions.gateway import PermissionViolationError

def run_mcp_tests():
    server = LocalMCPServer()
    register_default_tools(server)

    # 1. Test health check
    health = server.health()
    assert health["status"] == "healthy"
    assert "system_ping" in health["tools"]
    print(f"MCP Health Check Passed: {health}")

    # 2. Test safe tool execution
    ping_result = server.dispatch("system_ping")
    assert ping_result["status"] == "active"
    print(f"Tool Dispatch Success: {ping_result}")

    # 3. Test unauthorized/blocked capability injection
    server.register_tool(
        name="unauthorized_order_sim",
        func=lambda: "Should never run",
        description="Simulates malicious execution attempt",
        required_capability="EXECUTE"
    )
    
    try:
        server.dispatch("unauthorized_order_sim")
        raise AssertionError("Firewall failed to block EXECUTE tool!")
    except PermissionViolationError as e:
        print(f"Firewall Successfully Blocked Execution: {e}")

if __name__ == "__main__":
    run_mcp_tests()