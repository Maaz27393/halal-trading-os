from pydantic import BaseModel, Field
from typing import List, Optional

class MarketRegime(BaseModel):
    nifty_trend: str
    advance_decline: str
    india_vix: float
    global_cues: str
    sector_strength: List[str]
    market_bias: str
    confidence_evidence: str

class TradingEnvironment(BaseModel):
    environment_status: str  # Strong Go / Go / Neutral / No-Go
    applicable_conditions: List[str]
    risk_conditions: List[str]
    earnings_restrictions: List[str]
    warnings: List[str]

class ResearchWatchlistItem(BaseModel):
    candidate: str
    supporting_evidence: str
    technical_context: str
    fundamental_context: str
    retrieved_knowledge: str
    inclusion_exclusion_reason: str

class PreMarketBriefing(BaseModel):
    timestamp: str
    regime: MarketRegime
    environment: TradingEnvironment
    watchlist: List[ResearchWatchlistItem]
    provenance: List[str]