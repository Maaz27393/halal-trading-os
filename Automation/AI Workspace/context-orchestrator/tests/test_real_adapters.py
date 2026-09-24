from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from config import GRAPH_PATH, MEMORY_PATH, RETRIEVAL_SCRIPT
from contracts.context_contracts import ContextRequest
from providers.graphify.graphify_adapter import GraphifyProvider
from providers.memory.memory_adapter import MemoryProvider
from providers.obsidian.obsidian_adapter import ObsidianProvider


def print_result(result) -> None:
    print(f"\nProvider: {result.provider}")
    print(f"Status:   {result.status}")

    if result.success:
        print("Provenance:")
        print(result.provenance)
        print("Metadata:")
        print(result.metadata)
    else:
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")


def main() -> None:
    request = ContextRequest(
        user_query="How does retrieval find the relevant trading rule?",
        task_type="knowledge",
        required_sources=["obsidian"],
        optional_sources=["memory", "graphify"],
    )

    print("=" * 72)
    print("LOCAL AI - STEP 2A REAL PROVIDER ADAPTER TEST")
    print("=" * 72)

    print("\nConfigured paths:")
    print(f"Memory:   {MEMORY_PATH}")
    print(f"Obsidian: {RETRIEVAL_SCRIPT}")
    print(f"Graphify: {GRAPH_PATH}")

    providers = [
        MemoryProvider(MEMORY_PATH),
        ObsidianProvider(RETRIEVAL_SCRIPT),
        GraphifyProvider(GRAPH_PATH),
    ]

    for provider in providers:
        print("\n" + "-" * 72)
        print(f"{provider.name.upper()} ADAPTER")
        print("-" * 72)
        print(f"Capabilities: {provider.capabilities()}")
        print(f"Health:       {provider.health()}")

        result = provider.retrieve(request)
        print_result(result)

    print("\n" + "=" * 72)
    print("STEP 2A ADAPTER TEST COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
