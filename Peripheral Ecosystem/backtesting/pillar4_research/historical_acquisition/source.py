from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Set, Dict, Any, Optional

import pandas as pd


ALLOWED_ADJUSTMENT_STATUSES: Set[str] = {"RAW_UNADJUSTED"}


@dataclass(frozen=True)
class HistoricalBars:
    symbol: str
    start_date: str
    end_date: str
    dataframe: pd.DataFrame
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    timeframe: str = "1D"
    adjustment_status: str = "RAW_UNADJUSTED"
    raw_csv_bytes: Optional[bytes] = None
    provider: str = "yfinance"

    def __post_init__(self):
        if self.adjustment_status not in ALLOWED_ADJUSTMENT_STATUSES:
            raise ValueError(
                f"Unsupported adjustment mode '{self.adjustment_status}'. "
                f"Must be one of {ALLOWED_ADJUSTMENT_STATUSES}."
            )


class HistoricalDataSource(ABC):
    @abstractmethod
    def fetch_daily(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> HistoricalBars:
        pass
