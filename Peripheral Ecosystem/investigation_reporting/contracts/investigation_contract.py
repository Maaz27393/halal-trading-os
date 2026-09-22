from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    evidence_id: str
    source_domain: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content: str
    provenance: str
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

class InvestigationReport(BaseModel):
    investigation_id: str
    trigger: str
    time_window: str = "CURRENT"
    affected_domains: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    observed_facts: List[str] = Field(default_factory=list)
    derived_findings: List[str] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    data_quality_status: str = "UNKNOWN"
    system_status: str = "UNKNOWN"
    regression_status: str = "UNKNOWN"
    governance_status: str = "READ_ONLY"
    report_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    safety_governance: Dict[str, Any] = Field(default_factory=lambda: {
        "strictly_read_only_evidence": True,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })
