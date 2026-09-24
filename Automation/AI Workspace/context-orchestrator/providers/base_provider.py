from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from contracts.context_contracts import ContextRequest, ProviderResult


class ContextProvider(ABC):
    """
    Read-only provider contract.

    Providers retrieve and normalize context only.
    They do not make governance decisions.
    """

    name: str = "unknown"

    @abstractmethod
    def capabilities(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, request: ContextRequest) -> ProviderResult:
        raise NotImplementedError

    def health(self) -> bool:
        return True
