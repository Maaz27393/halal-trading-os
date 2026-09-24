from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class CapacityForecast(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    forecast_id: str
    target_component: str
    current_workload_metric: float
    projected_workload_metric: float
    time_horizon_days: int
    risk_state: str = Field(..., description="NORMAL, WATCH, CAPACITY_RISK, or CAPACITY_CRITICAL")
    confidence_score: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    governance_status: str = Field(default="PENDING_HUMAN_REVIEW", description="PENDING_HUMAN_REVIEW, PROPOSED_CHANGE, or REJECTED")
    security_boundary: Dict[str, Any] = Field(default_factory=lambda: {
        "analysis_only": True,
        "read_only": True,
        "automatic_scaling": False,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })
