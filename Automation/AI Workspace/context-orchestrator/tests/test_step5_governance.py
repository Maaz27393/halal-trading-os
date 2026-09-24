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
from governance.governance_gate import GovernanceGate
from model.qwen_runtime import QwenRuntime


def main() -> None:
    print("=" * 72)
    print("LOCAL AI - STEP 5 END-TO-END GOVERNANCE ORCHESTRATION TEST")
    print("=" * 72)

    # 1. Setup Registry with Real Providers
    registry = ProviderRegistry([
        MemoryProvider(MEMORY_PATH),
        ObsidianProvider(RETRIEVAL_SCRIPT),
        GraphifyProvider(GRAPH_PATH),
    ])

    # 2. Construct Request (Default sandbox profile)
    request = ContextRequest(
        user_query="How does retrieval find the relevant trading rule?",
        task_type="knowledge",
        required_sources=["obsidian"],
        optional_sources=["memory", "graphify"],
        governance_profile="sandbox",
    )

    print(f"\n[1] Request created for query: '{request.user_query}' (Profile: {request.governance_profile})")

    # 3. Router Dispatch
    router = ContextRouter(registry)
    provider_results = router.route(request)
    print(f"[2] Router dispatched to {len(provider_results)} providers.")

    # 4. Context Fusion
    bundle = ContextFusion.fuse(request, provider_results)
    print(f"[3] Context Fusion complete. Successful sources: {bundle.fused_context['sources_successful']}")

    # 5. Integrity Gate Validation
    validated_bundle = IntegrityGate.validate(bundle)
    print(f"[4] Integrity Gate Status: {validated_bundle.integrity_report['status']}")

    if not validated_bundle.is_valid:
        print("[X] Pipeline halted: Integrity Gate failed.")
        return

    # 6. Governance Gate Evaluation
    governed_bundle = GovernanceGate.evaluate(validated_bundle)
    gov_report = governed_bundle.governance_report
    print(f"[5] Governance Gate Status: {gov_report['status']} | Decision: {gov_report['decision']}")

    if not governed_bundle.is_valid:
        print(f"[X] Pipeline halted by Governance Gate. Violations: {gov_report.get('violations')}")
        return

    # 7. Qwen Runtime Generation
    print("[6] Invoking local Qwen runtime via Ollama (qwen3:4b)...")
    runtime = QwenRuntime(model_name="qwen3:4b")
    
    try:
        result = runtime.generate(governed_bundle)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'SUCCESS':
            print("\n--- QWEN GENERATED RESPONSE (GOVERNED) ---")
            print(result['response'])
            print("------------------------------------------")
            print("\nProvenance Traced:")
            for src, prov in result['provenance'].items():
                print(f"  - {src}: {prov['status']}")
        else:
            print("Errors:")
            for err in result.get('errors', []):
                print(f"  * {err}")
    except Exception as exc:
        print(f"[X] Runtime exception: {exc}")

    print("\n" + "=" * 72)
    print("STEP 5 GOVERNANCE ORCHESTRATION TEST COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
