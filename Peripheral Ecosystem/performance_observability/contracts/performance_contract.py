from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class PerformanceMetric(BaseModel):
    metric_id: str
    component: str
    operation: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float
    status: str = Field(..., description="SUCCESS or DEGRADED")
    record_count: int = 0
    resource_context: Dict[str, Any] = Field(default_factory=dict)
    provenance: str
    security_boundary: Dict[str, Any] = Field(default_factory=lambda: {
        "analysis_only": True,
        "read_only": True,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })

class CapacityThresholdReport(BaseModel):
    metric_id: str
    component: str
    operation: str
    observed_duration_ms: float
    baseline_duration_ms: float
    threshold_state: str = Field(..., description="NORMAL, ELEVATED, CAPACITY_WARNING, or CAPACITY_CRITICAL")
    bottleneck_breakdown: Dict[str, float] = Field(default_factory=dict)
    evaluation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
