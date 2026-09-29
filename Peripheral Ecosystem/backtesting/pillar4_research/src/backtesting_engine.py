from __future__ import annotations

import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.backtest_dataset import BacktestDataset

class StrategyContractError(Exception):
    """Raised when a strategy violates the StrategyContract."""
    pass

class StrategyContract(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def on_start(self, dataset: BacktestDataset) -> None:
        pass

    @abstractmethod
    def on_bar(self, bar_index: int, row: pd.Series) -> dict:
        pass

    @abstractmethod
    def on_finish(self) -> dict:
        pass

@dataclass(frozen=True)
class BacktestResult:
    strategy_name: str
    dataset_identity: str
    metrics: dict

class BacktestingEngine:
    def __init__(self, strategy: StrategyContract):
        self._validate_strategy(strategy)
        self._strategy = strategy

    @property
    def strategy(self) -> StrategyContract:
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: StrategyContract):
        self._validate_strategy(new_strategy)
        self._strategy = new_strategy

    def _validate_strategy(self, strategy: Any) -> None:
        # R15: Verify required contract methods and attributes exist
        required_attrs = ['name', 'on_start', 'on_bar', 'on_finish']
        for attr in required_attrs:
            if not hasattr(strategy, attr):
                raise StrategyContractError(f"Strategy missing required contract attribute/method: '{attr}'")
        
        # Verify name property is accessible
        try:
            strat_name = strategy.name
            if not isinstance(strat_name, str) or not strat_name.strip():
                raise StrategyContractError("Strategy 'name' property must return a non-empty string.")
        except Exception as e:
            if isinstance(e, StrategyContractError):
                raise
            raise StrategyContractError(f"Strategy 'name' evaluation failed: {e}") from e

    def run(self, dataset: BacktestDataset) -> BacktestResult:
        # R12, R13, R14: Strategy-agnostic orchestration over verified BacktestDataset
        if not isinstance(dataset, BacktestDataset):
            raise TypeError("BacktestingEngine requires a verified BacktestDataset instance.")

        # 1. Lifecycle initialization
        self._strategy.on_start(dataset)

        # 2. Iterate through historical observations in deterministic order
        df = dataset.df._df if hasattr(dataset.df, '_df') else dataset.df
        for idx, row in df.iterrows():
            self._strategy.on_bar(int(idx) if isinstance(idx, int) else 0, row)

        # 3. Lifecycle finalization & metrics gathering
        finish_metrics = self._strategy.on_finish()
        if not isinstance(finish_metrics, dict):
            finish_metrics = {"status": "COMPLETED"}

        return BacktestResult(
            strategy_name=self._strategy.name,
            dataset_identity=dataset.dataset_identity,
            metrics=finish_metrics
        )
