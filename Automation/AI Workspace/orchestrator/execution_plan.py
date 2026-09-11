from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ExecutionStep:
    step_id: str
    component_type: str  # "FIREWALL", "SKILL", "RETRIEVAL", "MEMORY"
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    required: bool = True

@dataclass
class ExecutionPlan:
    query: str
    intent: str
    authority_rank: int
    allowed_layers: List[str]
    permitted_tools: List[str]
    steps: List[ExecutionStep] = field(default_factory=list)
    is_valid: bool = True
    validation_error: Optional[str] = None
