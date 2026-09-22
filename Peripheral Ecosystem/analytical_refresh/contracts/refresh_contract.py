from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class RefreshTelemetryRecord(BaseModel):
    run_id: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    overall_status: str = Field(default="PENDING", description="PASS, FAIL, or BLOCKED")
    feeds_refreshed: List[str] = Field(default_factory=list)
    record_counts: Dict[str, int] = Field(default_factory=dict)
    validation_results: Dict[str, bool] = Field(default_factory=dict)
    failure_reason: Optional[str] = None
