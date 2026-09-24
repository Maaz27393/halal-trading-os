from __future__ import annotations

from typing import Dict, Iterable

from providers.base_provider import ContextProvider


class ProviderRegistry:
    """
    Simple provider registry.

    The registry knows provider capabilities, not provider-specific internals.
    """

    def __init__(self, providers: Iterable[ContextProvider] = ()):
        self._providers: Dict[str, ContextProvider] = {}

        for provider in providers:
            self.register(provider)

    def register(self, provider: ContextProvider) -> None:
        if provider.name in self._providers:
            raise ValueError(
                f"Provider already registered: {provider.name}"
            )

        self._providers[provider.name] = provider

    def get(self, name: str) -> ContextProvider | None:
        return self._providers.get(name)

    def names(self) -> list[str]:
        return sorted(self._providers)

    def capabilities(self) -> dict[str, list[str]]:
        return {
            name: provider.capabilities()
            for name, provider in self._providers.items()
        }
