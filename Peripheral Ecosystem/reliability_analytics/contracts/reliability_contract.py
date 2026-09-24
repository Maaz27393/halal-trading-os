from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class AnomalyEvent(BaseModel):
    anomaly_id: str
    component: str
    metric_name: str
    observed_value: float
    baseline_expected: float
    deviation_score: float
    severity_state: str = Field(..., description="NORMAL, UNUSUAL, ANOMALOUS, or EARLY_WARNING")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str
    security_boundary: Dict[str, Any] = Field(default_factory=lambda: {
        "analysis_only": True,
        "read_only": True,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })

class ReliabilityScorecard(BaseModel):
    component: str
    availability_ratio: float
    success_ratio: float
    quality_pass_ratio: float
    failure_frequency: float
    mean_recovery_duration_seconds: float
    evaluation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
