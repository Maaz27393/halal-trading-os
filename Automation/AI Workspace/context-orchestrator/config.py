from pathlib import Path


AI_WORKSPACE = Path(
    r"D:\OBSIDIAN VAULT\halal-trading-os\Automation\AI Workspace"
)

# Existing Retrieval V3.6
RETRIEVAL_SCRIPT = (
    AI_WORKSPACE
    / "Retrieval"
    / "vault_search.py"
)

# Set this to the actual persistent-memory JSON file.
MEMORY_PATH = (
    AI_WORKSPACE
    / "memory"
    / "memory.json"
)

# Set this to the actual Graphify graph artifact.
GRAPH_PATH = (
    AI_WORKSPACE
    / "experiments"
    / "graph-context"
    / "graphify"
    / "graph.json"
)
