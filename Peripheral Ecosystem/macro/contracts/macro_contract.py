from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class MacroIndicator(BaseModel):
    contract_version: str = Field(default="1.0.0", description="Canonical contract version")
    source_provider: str = Field(default="macro_provider", description="Provider origin identifier")
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of retrieval")
    indicator_name: str = Field(..., description="Name of macro indicator (e.g., REPO_RATE, CPI_INFLATION)")
    value: float = Field(..., description="Numeric indicator value")
    unit: str = Field(default="%", description="Measurement unit")
    period: str = Field(..., description="Reporting period (e.g., Q3 2026)")
    country: str = Field(default="India", description="Country context")
