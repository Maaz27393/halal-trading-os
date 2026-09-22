from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class AlertEvent(BaseModel):
    alert_id: str
    investigation_id: str
    severity: str = Field(..., description="INFO, WARNING, or CRITICAL")
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    summary: str
    report_reference: str
    provenance: str
    delivery_policy: Dict[str, Any] = Field(default_factory=dict)
    security_boundary: Dict[str, Any] = Field(default_factory=lambda: {
        "notification_capability": True,
        "execution_capability": "NONE",
        "order_capability": "NONE",
        "live_auto_execution": False,
        "outbound_only": True
    })
