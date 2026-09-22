from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class QualityState(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    INCOMPLETE = "INCOMPLETE"
    INVALID = "INVALID"
    VALID = "VALID"

class DataQualityMetadata(BaseModel):
    provider: str
    retrieval_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_timestamp: Optional[datetime] = None
    contract_version: str = "1.0.0"
    validation_status: QualityState = QualityState.VALID
    missing_fields: List[str] = Field(default_factory=list)
    freshness_status: QualityState = QualityState.FRESH
    provenance: Dict[str, Any] = Field(default_factory=dict)
    validation_errors: List[str] = Field(default_factory=list)
    governance_flag: bool = Field(default=False, description="Must always be FALSE")
