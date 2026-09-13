from pydantic import BaseModel
from typing import List, Optional

class ShadowTradeRecord(BaseModel):
    trade_id: str
    symbol: str
    entry_price: float
    exit_price: float
    quantity: int
    transaction_type: str
    realized_pnl: float
    slippage_pct: float
    risk_reward_realized: float
    compliance_checked: bool

class AttributionSummary(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    total_realized_pnl: float
    average_slippage_pct: float
    average_rr: float

class JournalReport(BaseModel):
    timestamp: str
    summary: AttributionSummary
    trades: List[ShadowTradeRecord]
    provenance: List[str]