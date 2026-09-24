from __future__ import annotations

from typing import List

from contracts.context_contracts import ContextRequest, ProviderResult
from providers.provider_registry import ProviderRegistry


class ContextRouter:
    """
    Routes a ContextRequest to the appropriate registered providers
    based on required and optional sources.
    """

    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

    def route(self, request: ContextRequest) -> List[ProviderResult]:
        target_names: set[str] = set()

        # Gather required sources
        for source in request.required_sources:
            if self.registry.get(source):
                target_names.add(source)

        # Gather optional sources
        for source in request.optional_sources:
            if self.registry.get(source):
                target_names.add(source)

        # Fallback: if no sources specified, query all available providers
        if not target_names:
            target_names = set(self.registry.names())

        results: List[ProviderResult] = []

        for name in sorted(target_names):
            provider = self.registry.get(name)
            if not provider:
                results.append(
                    ProviderResult(
                        provider=name,
                        status="UNAVAILABLE",
                        query=request.user_query,
                        content={},
                        errors=[f"Provider '{name}' is registered in request but missing from registry."],
                    )
                )
                continue

            try:
                result = provider.retrieve(request)
                results.append(result)
            except Exception as exc:
                results.append(
                    ProviderResult(
                        provider=name,
                        status="ERROR",
                        query=request.user_query,
                        content={},
                        errors=[f"Provider exception during retrieval: {exc}"],
                    )
                )

        return results
