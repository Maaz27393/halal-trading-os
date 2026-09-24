from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class OperationalAcceptanceResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    acceptance_id: str
    acceptance_status: str = Field(..., description="ACCEPTED, ACCEPTED_WITH_WARNINGS, or NOT_ACCEPTED")
    hardening_checks: Dict[str, str]
    baseline_summary: Dict[str, Any]
    security_audit_passed: bool = True
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
