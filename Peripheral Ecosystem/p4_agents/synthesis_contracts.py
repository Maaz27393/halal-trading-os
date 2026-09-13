from pydantic import BaseModel, Field
from typing import List, Optional

class TechnicalMetrics(BaseModel):
    symbol: str
    rsi: float
    ema_alignment: str  # e.g., "Bullish (20 > 50)"
    volume_spike: bool
    support_distance_pct: float

class FundamentalMetrics(BaseModel):
    symbol: str
    roe: float
    debt_to_equity: float
    compliance_status: str  # e.g., "Compliant / Halal Verified"
    quarterly_growth_pct: float

class SynthesisItem(BaseModel):
    symbol: str
    verdict: str  # e.g., "High Conviction", "Watchlist", "Filtered Out"
    technical: TechnicalMetrics
    fundamental: FundamentalMetrics
    retrieved_insight: str
    synthesis_rationale: str

class SynthesisReport(BaseModel):
    timestamp: str
    total_screened: int
    qualified_count: int
    synthesis_items: List[SynthesisItem]
    provenance: List[str]