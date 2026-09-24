from __future__ import annotations

from typing import Any, Dict, List

from contracts.context_contracts import ContextBundle, ContextRequest, ProviderResult


class ContextFusion:
    """
    Fuses multiple ProviderResults into a single normalized ContextBundle,
    preserving provenance and separating domain contexts.
    """

    @staticmethod
    def fuse(request: ContextRequest, provider_results: List[ProviderResult]) -> ContextBundle:
        memory_data: Any = {}
        knowledge_data: Any = {}
        code_data: Any = {}
        provenance_map: Dict[str, Any] = {}

        for res in provider_results:
            provenance_map[res.provider] = {
                "status": res.status,
                "provenance": res.provenance,
                "metadata": res.metadata,
                "errors": res.errors,
            }

            if not res.success:
                continue

            if res.provider == "memory":
                memory_data = res.content
            elif res.provider == "obsidian":
                knowledge_data = res.content
            elif res.provider == "graphify":
                code_data = res.content
            else:
                # Generic fallback storage
                provenance_map[res.provider]["raw_content"] = res.content

        fused_summary = {
            "query": request.user_query,
            "task_type": request.task_type,
            "sources_queried": [r.provider for r in provider_results],
            "sources_successful": [r.provider for r in provider_results if r.success],
        }

        return ContextBundle(
            request=request,
            providers=provider_results,
            memory_context=memory_data,
            knowledge_context=knowledge_data,
            code_context=code_data,
            fused_context=fused_summary,
            provenance=provenance_map,
        )
