from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ScenarioResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    scenario_id: str
    scenario_name: str
    baseline_metrics: Dict[str, float]
    projected_metrics: Dict[str, float]
    assumptions: List[str]
    sensitivity_rankings: Dict[str, float]
    confidence_score: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    governance_status: str = Field(default="PENDING_HUMAN_REVIEW", description="PENDING_HUMAN_REVIEW, PROPOSED_CHANGE, or REJECTED")
    security_boundary: Dict[str, Any] = Field(default_factory=lambda: {
        "analysis_only": True,
        "read_only": True,
        "automatic_remediation": False,
        "automatic_scaling": False,
        "automatic_decision": False,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })
