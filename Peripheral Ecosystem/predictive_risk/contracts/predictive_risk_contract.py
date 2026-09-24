from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class PredictiveRiskIndicator(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    risk_id: str
    risk_category: str
    affected_domain: str
    risk_level: str = Field(..., description="LOW_RISK, WATCH, ELEVATED, HIGH_RISK, or CRITICAL")
    horizon: str = Field(..., description="current, short_term, or medium_term")
    observed_indicators: List[str]
    historical_patterns: List[str]
    confidence_score: float
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
