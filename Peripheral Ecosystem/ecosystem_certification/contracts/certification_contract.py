from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class EcosystemCertificationResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    certification_id: str
    subsystem_statuses: Dict[str, str]
    overall_status: str = Field(..., description="CERTIFIED, CERTIFIED_WITH_WARNINGS, or FAILED")
    epistemic_integrity: bool = True
    governance_integrity: bool = True
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
