from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from contracts.context_contracts import ContextRequest, ProviderResult
from providers.base_provider import ContextProvider


class MemoryProvider(ContextProvider):
    """
    Read-only adapter for local persistent memory.

    Expected JSON structure is intentionally flexible. The adapter preserves
    the stored JSON rather than imposing a domain-specific memory schema.
    """

    name = "memory"

    def __init__(self, memory_path: str | Path):
        self.memory_path = Path(memory_path)

    def capabilities(self) -> List[str]:
        return [
            "persistent_memory",
            "user_state",
            "workflow_state",
            "preferences",
        ]

    def health(self) -> bool:
        return self.memory_path.exists() and self.memory_path.is_file()

    def retrieve(self, request: ContextRequest) -> ProviderResult:
        if not self.memory_path.exists():
            return ProviderResult(
                provider=self.name,
                status="UNAVAILABLE",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "local_memory",
                    "path": str(self.memory_path),
                },
                errors=[f"Memory file not found: {self.memory_path}"],
            )

        try:
            with self.memory_path.open("r", encoding="utf-8") as handle:
                data: Any = json.load(handle)

            return ProviderResult(
                provider=self.name,
                status="SUCCESS",
                query=request.user_query,
                content=data,
                provenance={
                    "source_type": "local_memory",
                    "path": str(self.memory_path),
                    "read_only": True,
                },
                metadata={
                    "format": "json",
                },
            )

        except json.JSONDecodeError as exc:
            return ProviderResult(
                provider=self.name,
                status="ERROR",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "local_memory",
                    "path": str(self.memory_path),
                },
                errors=[f"Invalid JSON: {exc}"],
            )

        except OSError as exc:
            return ProviderResult(
                provider=self.name,
                status="ERROR",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "local_memory",
                    "path": str(self.memory_path),
                },
                errors=[str(exc)],
            )
