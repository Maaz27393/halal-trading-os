from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SessionState(str, Enum):
    VALID = "VALID"
    EXPIRING = "EXPIRING"
    EXPIRED = "EXPIRED"
    REAUTH_REQUIRED = "REAUTH_REQUIRED"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"

class SessionMetadata(BaseModel):
    contract_version: str = Field(default="1.0.0", description="Session contract version")
    provider_id: str = Field(..., description="Unique identifier of the provider")
    session_state: SessionState = Field(default=SessionState.UNAVAILABLE, description="Current lifecycle state")
    authenticated: bool = Field(default=False, description="True if credentials are active and verified")
    expires_at: Optional[datetime] = Field(default=None, description="Timestamp when session expires")
    last_validated_at: Optional[datetime] = Field(default=None, description="Last successful/attempted validation time")
    last_success: Optional[datetime] = Field(default=None, description="Timestamp of last successful operation")
    last_failure: Optional[datetime] = Field(default=None, description="Timestamp of last failure")
    failure_reason: Optional[str] = Field(default=None, description="Detailed failure message or reason code")
    reauth_required: bool = Field(default=False, description="Fail-closed flag requiring re-authentication")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific health/status attributes")
