from pydantic import BaseModel
from typing import List, Optional

class SessionSummary(BaseModel):
    date: str
    nifty_close: float
    market_breadth_ratio: float
    total_shadow_turnover: float
    key_sector_leader: str

class StrategyHypothesis(BaseModel):
    strategy_name: str
    backtest_win_rate_pct: float
    profit_factor: float
    max_drawdown_pct: float
    hypothesis_status: str  # e.g., "Approved for Paper Forward Testing", "Refinement Required"
    rationale: str

    class Config:
        arbitrary_types_allowed = True

class PostMarketReport(BaseModel):
    timestamp: str
    session: SessionSummary
    strategy_evaluations: List[StrategyHypothesis]
    retrieved_insights: str
    provenance: List[str]