from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ContextRequest:
    user_query: str
    task_type: str = "general"
    required_sources: List[str] = field(default_factory=list)
    optional_sources: List[str] = field(default_factory=list)
    required_symbols: List[str] = field(default_factory=list)
    required_paths: List[str] = field(default_factory=list)
    governance_profile: str = "sandbox"


@dataclass
class ProviderResult:
    provider: str
    status: str
    query: str
    content: Any
    provenance: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.status == "SUCCESS"


@dataclass
class ContextBundle:
    request: ContextRequest
    providers: List[ProviderResult] = field(default_factory=list)
    memory_context: Any = field(default_factory=dict)
    knowledge_context: Any = field(default_factory=dict)
    code_context: Any = field(default_factory=dict)
    fused_context: Dict[str, Any] = field(default_factory=dict)
    optimization_report: Dict[str, Any] = field(default_factory=dict)
    integrity_report: Dict[str, Any] = field(default_factory=dict)
    governance_context: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.integrity_report.get("status") == "VALID"

    def successful_results(self) -> List[ProviderResult]:
        return [p for p in self.providers if p.success]

    def failed_results(self) -> List[ProviderResult]:
        return [p for p in self.providers if not p.success]
