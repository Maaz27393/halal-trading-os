from pydantic import BaseModel
from typing import List, Optional

class EarningsRiskItem(BaseModel):
    symbol: str
    earnings_date: str
    days_to_earnings: int
    risk_level: str  # e.g., "High", "Moderate", "Low"
    actionable_restriction: str

class NewsIntelligenceItem(BaseModel):
    headline: str
    source: str
    sentiment: str  # e.g., "Bullish", "Bearish", "Neutral"
    impact_score: float  # 0.0 to 1.0
    relevant_symbols: List[str]

class NewsRiskAssessmentReport(BaseModel):
    timestamp: str
    earnings_risks: List[EarningsRiskItem]
    news_intelligence: List[NewsIntelligenceItem]
    macro_warnings: List[str]
    provenance: List[str]