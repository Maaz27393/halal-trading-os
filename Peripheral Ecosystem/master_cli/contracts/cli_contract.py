from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class AuditLogRecord(BaseModel):
    audit_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    command: str = Field(..., description="STATUS, REFRESH, CERTIFY, or AUDIT")
    status: str = Field(..., description="PASS, FAIL, or BLOCKED")
    details: Dict[str, Any] = Field(default_factory=dict)
    safety_invariants: Dict[str, Any] = Field(default_factory=lambda: {
        "read_only": True,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })
