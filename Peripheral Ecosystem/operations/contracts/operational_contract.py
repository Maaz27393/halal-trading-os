from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class OperationalEvent(BaseModel):
    event_id: str
    event_type: str = Field(..., description="SESSION_EVENT, PROVIDER_EVENT, DATA_EVENT, PIPELINE_EVENT, BACKTEST_EVENT, ANALYTICS_EVENT, GOVERNANCE_EVENT, SYSTEM_EVENT")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_domain: str
    status: str = Field(..., description="SUCCESS, WARNING, FAILED, CONTAINED")
    governance_flag: bool = Field(default=False, description="Must always be FALSE")
    details: Dict[str, Any] = Field(default_factory=dict)
