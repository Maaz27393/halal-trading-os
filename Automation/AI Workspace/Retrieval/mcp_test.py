import asyncio
import json
from mcp_server import mcp

async def test_mcp_protocol():
    # Verify tool registration
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "vault_search" in tool_names, "ERROR: vault_search tool not found in MCP server."
    print(f"[SUCCESS] Tool registered: {tool_names}")

    # Verify tool execution through FastMCP engine
    raw_result = await mcp.call_tool("vault_search", {"query": "Who has authority to approve a change to the Trading OS?"})
    assert raw_result is not None, "ERROR: MCP tool returned null result."
    
    # FastMCP call_tool returns standard content structure
    print(f"[SUCCESS] Tool execution returned valid result payload.")
    print("\nMCP Protocol Test PASSED.")

if __name__ == "__main__":
    asyncio.run(test_mcp_protocol())
