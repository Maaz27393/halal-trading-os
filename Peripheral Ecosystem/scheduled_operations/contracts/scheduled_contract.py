from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ScheduledRunTelemetry(BaseModel):
    run_id: str
    trigger_type: str = Field(..., description="MANUAL or SCHEDULED")
    scheduled_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actual_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actual_end: Optional[datetime] = None
    duration_seconds: float = 0.0
    lifecycle_status: str = Field(default="IDLE", description="IDLE, SCHEDULED, RUNNING, VALIDATING, PUBLISHED, COMPLETED, FAILED")
    feed_results: List[str] = Field(default_factory=list)
    validation_results: Dict[str, bool] = Field(default_factory=dict)
    publication_result: bool = False
    error_information: Optional[str] = None
    overall_status: str = Field(default="PENDING")
    safeguards: Dict[str, Any] = Field(default_factory=lambda: {
        "read_only": True,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })
