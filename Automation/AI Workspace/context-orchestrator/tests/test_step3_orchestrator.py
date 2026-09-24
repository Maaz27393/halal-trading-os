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
from providers.provider_registry import ProviderRegistry
from router.context_router import ContextRouter
from fusion.context_fusion import ContextFusion
from integrity.integrity_gate import IntegrityGate


def main() -> None:
    print("=" * 72)
    print("LOCAL AI - STEP 3 CONTEXT ORCHESTRATOR FOUNDATION TEST")
    print("=" * 72)

    # 1. Setup Registry with Real Providers
    registry = ProviderRegistry([
        MemoryProvider(MEMORY_PATH),
        ObsidianProvider(RETRIEVAL_SCRIPT),
        GraphifyProvider(GRAPH_PATH),
    ])

    # 2. Construct Request (requiring obsidian, optional memory/graphify)
    request = ContextRequest(
        user_query="How does retrieval find the relevant trading rule?",
        task_type="knowledge",
        required_sources=["obsidian"],
        optional_sources=["memory", "graphify"],
        governance_profile="sandbox",
    )

    print(f"\n[1] Request created for query: '{request.user_query}'")
    print(f"    Required sources: {request.required_sources}")
    print(f"    Optional sources: {request.optional_sources}")

    # 3. Router Dispatch
    router = ContextRouter(registry)
    provider_results = router.route(request)
    print(f"\n[2] Router dispatched to {len(provider_results)} providers:")
    for res in provider_results:
        print(f"    - {res.provider}: {res.status}")

    # 4. Context Fusion
    bundle = ContextFusion.fuse(request, provider_results)
    print(f"\n[3] Context Fusion complete. Successful sources: {bundle.fused_context['sources_successful']}")

    # 5. Integrity Gate Validation
    validated_bundle = IntegrityGate.validate(bundle)
    report = validated_bundle.integrity_report
    print(f"\n[4] Integrity Gate Validation:")
    print(f"    Status: {report['status']}")
    for check in report['checks']:
        print(f"    - Check '{check['check']}': {check['status']}")

    if report['errors']:
        print("    Errors:")
        for err in report['errors']:
            print(f"      * {err}")

    print("\n" + "=" * 72)
    print(f"ORCHESTRATION PIPELINE RESULT: {'SUCCESS' if validated_bundle.is_valid else 'FAILED'}")
    print("=" * 72)


if __name__ == "__main__":
    main()
