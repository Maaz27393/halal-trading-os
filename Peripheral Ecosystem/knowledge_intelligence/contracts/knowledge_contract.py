from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class KnowledgeObject(BaseModel):
    object_id: str
    domain: str = Field(..., description="REGRESSION, CONTROL_CENTER, REFRESH, AUDIT, or DATA_QUALITY")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    title: str
    content: str
    provenance_source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DecisionContextPackage(BaseModel):
    investigation_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    query_topic: str
    relevant_facts: List[KnowledgeObject] = Field(default_factory=list)
    historical_records: List[KnowledgeObject] = Field(default_factory=list)
    derived_analysis: List[str] = Field(default_factory=list)
    safety_guarantee: str = Field(default="STRICTLY_READ_ONLY_EVIDENCE")
