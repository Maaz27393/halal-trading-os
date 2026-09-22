from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class PhaseResult(BaseModel):
    phase_number: int
    phase_name: str
    status: str = Field(..., description="PASS, FAIL, or BLOCKED")
    details: Dict[str, Any] = Field(default_factory=dict)

class CrossPhaseResult(BaseModel):
    source_phase: int
    target_phase: int
    contract_name: str
    status: str = Field(..., description="VALIDATED or FAILED")
    notes: str

class FailureInjectionResult(BaseModel):
    injection_type: str
    target_domain: str
    expected_behavior: str
    observed_behavior: str
    status: str = Field(..., description="SAFE_CONTAINMENT or BREACH")

class E2ERunResult(BaseModel):
    run_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    overall_status: str = "PENDING"
    phase_results: List[PhaseResult] = Field(default_factory=list)
    cross_phase_results: List[CrossPhaseResult] = Field(default_factory=list)
    failure_injections: List[FailureInjectionResult] = Field(default_factory=list)
    governance_state: Dict[str, Any] = Field(default_factory=lambda: {
        "read_only": True,
        "live_auto_execution": False,
        "order_capability": "NONE",
        "execution_authority": "NONE"
    })
    certification_gate: str = "PENDING"
