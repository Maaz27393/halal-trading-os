from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class DashboardState(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    system_overview: Dict[str, Any] = Field(default_factory=dict)
    provider_health: Dict[str, str] = Field(default_factory=dict)
    data_quality: Dict[str, Any] = Field(default_factory=dict)
    governance: Dict[str, Any] = Field(default_factory=dict)
    refresh_operations: Dict[str, Any] = Field(default_factory=dict)
    certification: Dict[str, Any] = Field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    safety_guarantee: str = Field(default="STRICTLY_READ_ONLY")
