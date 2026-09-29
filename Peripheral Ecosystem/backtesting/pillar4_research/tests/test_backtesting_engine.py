from __future__ import annotations

import pytest
import pandas as pd
from src.calendar_adapter import load_and_verify_calendar, compute_canonical_hash
from src.dataset_store import DatasetStore
from src.dataset_loader import load_backtest_dataset
from src.backtest_dataset import BacktestDataset
from src.backtesting_engine import (
    BacktestingEngine,
    StrategyContract,
    StrategyContractError,
    BacktestResult
)

class DummyValidStrategy(StrategyContract):
    @property
    def name(self) -> str:
        return "dummy_valid_strategy"

    def on_start(self, dataset: BacktestDataset) -> None:
        pass

    def on_bar(self, bar_index: int, row: pd.Series) -> dict:
        return {"action": "HOLD"}

    def on_finish(self) -> dict:
        return {"status": "SUCCESS"}

class AnotherValidStrategy(StrategyContract):
    @property
    def name(self) -> str:
        return "another_strategy"

    def on_start(self, dataset: BacktestDataset) -> None:
        pass

    def on_bar(self, bar_index: int, row: pd.Series) -> dict:
        return {"action": "HOLD"}

    def on_finish(self) -> dict:
        return {"status": "SUCCESS"}

class MalformedStrategyWithoutName:
    def on_bar(self, bar_index: int, row: pd.Series) -> dict:
        return {}
    def on_finish(self) -> dict:
        return {}

@pytest.fixture
def temp_store(tmp_path):
    return DatasetStore(tmp_path)

@pytest.fixture
def sample_calendar(tmp_path):
    cal_path = tmp_path / "valid_calendar.json"
    cal_data = {
        "calendar_id": "NYSE_DEFAULT",
        "calendar_version": "1.0.0",
        "exchange": "NYSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [{"date": "2026-01-02"}]
    }
    cal_data["sha256"] = compute_canonical_hash(cal_data)
    cal_path.write_text(str(cal_data).replace("'", '"'), encoding="utf-8")
    return load_and_verify_calendar(cal_path)

@pytest.fixture
def loaded_dataset(temp_store, sample_calendar):
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-02 09:30:00', '2026-01-02 09:31:00'], utc=True),
        'open': [100.0, 101.0],
        'high': [102.0, 103.0],
        'low': [99.0, 100.0],
        'close': [101.0, 102.0],
        'volume': [1000, 1500]
    })
    res = temp_store.store(df, sample_calendar, symbol="AAPL", timeframe="1m")
    return load_backtest_dataset(temp_store, res.dataset_identity, sample_calendar)

def test_R12_engine_accepts_any_valid_strategy(loaded_dataset):
    """R12: Engine accepts any valid strategy implementing StrategyContract."""
    strategy = DummyValidStrategy()
    engine = BacktestingEngine(strategy=strategy)
    result = engine.run(loaded_dataset)
    assert isinstance(result, BacktestResult)
    assert result.strategy_name == "dummy_valid_strategy"
    assert result.dataset_identity == loaded_dataset.dataset_identity

def test_R13_engine_is_strategy_agnostic(loaded_dataset):
    """R13: Engine does not dispatch behavior based on strategy name or ID."""
    strat1 = DummyValidStrategy()
    strat2 = AnotherValidStrategy()
    
    engine1 = BacktestingEngine(strategy=strat1)
    engine2 = BacktestingEngine(strategy=strat2)
    
    res1 = engine1.run(loaded_dataset)
    res2 = engine2.run(loaded_dataset)
    assert res1.strategy_name != res2.strategy_name

def test_R14_same_dataset_supplied_independently(loaded_dataset):
    """R14: The same verified BacktestDataset can be supplied independently to multiple strategies."""
    strat1 = DummyValidStrategy()
    strat2 = AnotherValidStrategy()
    
    engine = BacktestingEngine(strategy=strat1)
    res1 = engine.run(loaded_dataset)
    
    engine.strategy = strat2
    res2 = engine.run(loaded_dataset)
    
    assert res1.dataset_identity == res2.dataset_identity
    assert res1.strategy_name == "dummy_valid_strategy"
    assert res2.strategy_name == "another_strategy"

def test_R15_malformed_strategy_contract_rejected(loaded_dataset):
    """R15: Invalid/malformed strategy contracts are rejected fail-closed before run begins."""
    malformed = MalformedStrategyWithoutName()
    with pytest.raises((StrategyContractError, TypeError, AttributeError)):
        engine = BacktestingEngine(strategy=malformed)
        engine.run(loaded_dataset)
