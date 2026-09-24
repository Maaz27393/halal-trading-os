"""
Canonical OHLCV and Bar Contract definitions.
Provider-neutral market data representation for backtesting.
"""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OHLCVBar:
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    session_closed: bool = False
