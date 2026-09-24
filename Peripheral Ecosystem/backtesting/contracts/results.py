"""
Backtest Results and Attribution Contracts.
Standardized output contracts for reporting and Power BI ingestion.
"""
from dataclasses import dataclass

@dataclass
class BacktestResult:
    strategy_id: str
    symbol: str
    total_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
