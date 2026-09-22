from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class OHLCVBar(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class TradeSignal(BaseModel):
    symbol: str
    entry_time: datetime
    entry_price: float
    direction: str = Field(..., description="LONG or SHORT")
    stop_loss: float
    target_price: float

class TradeResult(BaseModel):
    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    direction: str
    pnl: float
    pnl_percentage: float
    outcome: str = Field(..., description="TARGET_HIT, STOP_LOSS_HIT, or EXPIRED")

class BacktestReport(BaseModel):
    strategy_name: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    net_pnl: float
    max_drawdown: float
    trades: List[TradeResult] = Field(default_factory=list)
