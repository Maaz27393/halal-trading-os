from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import pandas as pd

@dataclass
class HistoricalBars:
    symbol: str
    start_date: str
    end_date: str
    dataframe: pd.DataFrame
    source_metadata: dict[str, Any] = field(default_factory=dict)

class HistoricalDataSource(ABC):
    @abstractmethod
    def fetch_daily(self, symbol: str, start_date: str, end_date: str) -> HistoricalBars:
        """Fetch daily historical OHLCV observations."""
        raise NotImplementedError
