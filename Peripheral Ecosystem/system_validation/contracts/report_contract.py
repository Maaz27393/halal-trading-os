from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class GovernanceState(BaseModel):
    live_auto_execution: bool = False
    order_capability: str = "NONE"
    execution_authority: str = "NONE"

class CertificationReport(BaseModel):
    run_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    baseline: str = "phase18-certified"
    overall_status: str = Field(..., description="PASS, FAIL, or BLOCKED")
    domains: Dict[str, str] = Field(default_factory=dict)
    governance: GovernanceState = Field(default_factory=GovernanceState)
    failures: List[str] = Field(default_factory=list)
