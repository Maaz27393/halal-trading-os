from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class GovernanceInfo(BaseModel):
    live_auto_execution: bool = Field(default=False)
    order_capability: str = Field(default="NONE")
    execution_authority: str = Field(default="NONE")
    governance_mode: str = Field(default="READ_ONLY")

class EcosystemStatusSummary(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    system_status: str = Field(..., description="HEALTHY, DEGRADED, or FAILING")
    regression_status: str = Field(..., description="PASS, FAIL, or BLOCKED")
    data_quality_status: str = Field(..., description="PASS, FAIL, or DEGRADED")
    governance: GovernanceInfo = Field(default_factory=GovernanceInfo)
    providers: Dict[str, str] = Field(default_factory=dict)
    active_alerts: int = Field(default=0)
    data_quality_issues: int = Field(default=0)
    critical_failures: int = Field(default=0)
    failures_log: List[str] = Field(default_factory=list)
