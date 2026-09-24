from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class OptimizationCandidate(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    candidate_id: str
    target_component: str
    bottleneck_description: str
    baseline_duration_ms: float
    projected_duration_ms: float
    estimated_impact_percentage: float
    confidence_score: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    governance_status: str = Field(default="PENDING_HUMAN_REVIEW", description="PENDING_HUMAN_REVIEW, PROPOSED_CHANGE, or REJECTED")
    security_boundary: Dict[str, Any] = Field(default_factory=lambda: {
        "analysis_only": True,
        "read_only": True,
        "automatic_remediation": False,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })

class BenchmarkComparison(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    benchmark_id: str
    component: str
    baseline_ms: float
    optimized_ms: float
    improvement_percentage: float
    status: str = Field(..., description="BENEFICIAL, NEUTRAL, or REGRESSION")
