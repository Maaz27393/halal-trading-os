from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class RootCauseCandidate(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    root_cause_id: str
    affected_domain: str
    candidate_cause: str
    relationship_type: str = Field(default="CANDIDATE_CAUSE", description="OBSERVED, TEMPORAL_ASSOCIATION, CORRELATED, CANDIDATE_CAUSE, or UNCONFIRMED")
    supporting_observations: List[str]
    correlated_signals: List[str]
    contradictory_evidence: List[str] = Field(default_factory=list)
    confidence_score: float
    investigation_status: str = Field(default="PENDING_HUMAN_REVIEW")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
