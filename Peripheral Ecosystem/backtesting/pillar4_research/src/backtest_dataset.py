from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from src.calendar_adapter import CalendarMetadata

class DatasetMutationError(Exception):
    """Raised when an unauthorized mutation is attempted on a frozen BacktestDataset."""
    pass

class ImmutableDataFrame:
    """Read-only proxy wrapping a pandas DataFrame to enforce R10 & R11 contracts."""
    def __init__(self, df: pd.DataFrame):
        required_cols = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Dataset missing required OHLCV columns: {required_cols - set(df.columns)}")
        
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            
        self._df = df.copy(deep=True)
        for col in self._df.columns:
            if pd.api.types.is_numeric_dtype(self._df[col]):
                try:
                    self._df[col].values.flags.writeable = False
                except Exception:
                    pass

    @property
    def columns(self):
        return self._df.columns

    @property
    def shape(self):
        return self._df.shape

    @property
    def dtypes(self):
        return self._df.dtypes

    def __getitem__(self, key):
        res = self._df[key]
        if isinstance(res, pd.DataFrame):
            return ImmutableDataFrame(res)
        return res

    def __setitem__(self, key, value):
        raise DatasetMutationError("BacktestDataset DataFrame is immutable and cannot be mutated downstream.")

    def __setdelitem__(self, key):
        raise DatasetMutationError("BacktestDataset DataFrame is immutable and cannot be mutated downstream.")

    def __getattr__(self, name):
        attr = getattr(self._df, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                res = attr(*args, **kwargs)
                if isinstance(res, pd.DataFrame):
                    return ImmutableDataFrame(res)
                return res
            return wrapper
        return attr

    def __repr__(self):
        return repr(self._df)

    def __str__(self):
        return str(self._df)

@dataclass(frozen=True)
class BacktestDataset:
    dataset_identity: str
    dataset_sha256: str
    calendar_sha256: str
    df: ImmutableDataFrame | pd.DataFrame
    calendar_metadata: CalendarMetadata

    def __post_init__(self):
        if not isinstance(self.df, ImmutableDataFrame):
            object.__setattr__(self, 'df', ImmutableDataFrame(self.df))
