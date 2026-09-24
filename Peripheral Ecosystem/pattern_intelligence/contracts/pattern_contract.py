from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class OperationalPattern(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    pattern_id: str
    source_domains: List[str]
    pattern_name: str
    description: str
    occurrence_count: int
    confidence_score: float
    regime_state: str = Field(..., description="NORMAL, DEGRADED, HIGH_LOAD, CAPACITY_RISK, or RECOVERY")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    governance_status: str = Field(default="PENDING_HUMAN_REVIEW", description="PENDING_HUMAN_REVIEW, PROPOSED_CHANGE, or REJECTED")
    security_boundary: Dict[str, Any] = Field(default_factory=lambda: {
        "analysis_only": True,
        "read_only": True,
        "automatic_remediation": False,
        "automatic_scaling": False,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })
