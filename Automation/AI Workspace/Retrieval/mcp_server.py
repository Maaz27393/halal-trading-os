from fastmcp import FastMCP
import retrieval_adapter

# Initialize FastMCP Server
mcp = FastMCP("Halal Trading OS Vault Search")

@mcp.tool()
def vault_search(query: str, max_results: int = 10) -> dict:
    """
    Searches the Halal Trading OS Obsidian vault for rules, governance, strategies, and research evidence.
    
    Args:
        query: The search query or question to retrieve context for.
        max_results: Maximum number of ranked search results to return (default: 10).
    """
    return retrieval_adapter.query_retrieval_api(query=query, max_results=max_results)

if __name__ == "__main__":
    mcp.run()
