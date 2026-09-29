from __future__ import annotations

import pytest
import pandas as pd
from src.calendar_adapter import load_and_verify_calendar, compute_canonical_hash
from src.dataset_store import DatasetStore
from src.dataset_loader import load_backtest_dataset
from src.backtest_dataset import BacktestDataset
from src.backtesting_engine import BacktestingEngine, StrategyContract, StrategyContractError

class StatefulStrategy(StrategyContract):
    def __init__(self):
        self.run_count = 0
        self.seen_bars = []

    @property
    def name(self) -> str:
        return "stateful_strategy"

    def on_start(self, dataset: BacktestDataset) -> None:
        self.run_count += 1
        self.seen_bars.clear()

    def on_bar(self, bar_index: int, row: pd.Series) -> dict:
        self.seen_bars.append(bar_index)
        return {"action": "HOLD"}

    def on_finish(self) -> dict:
        return {"run_count": self.run_count, "bars_processed": len(self.seen_bars)}

class IntrusiveStrategy(StrategyContract):
    """A malformed strategy attempting to access restricted infrastructure."""
    @property
    def name(self) -> str:
        return "intrusive_strategy"

    def on_start(self, dataset: BacktestDataset) -> None:
        # R17 violation attempt: Trying to check if dataset or environment exposes store handles
        if hasattr(dataset, 'store') or hasattr(dataset, 'load'):
            raise PermissionError("Direct store access detected!")

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

def test_R16_strategy_receives_data_only_through_contract(loaded_dataset):
    """R16: Strategy receives historical data and context strictly via engine-provided contract methods."""
    class PureContractStrategy(StrategyContract):
        @property
        def name(self) -> str:
            return "pure_contract"
        def on_start(self, dataset: BacktestDataset) -> None:
            assert isinstance(dataset, BacktestDataset)
        def on_bar(self, bar_index: int, row: pd.Series) -> dict:
            assert isinstance(row, pd.Series)
            assert 'close' in row
            return {"action": "HOLD"}
        def on_finish(self) -> dict:
            return {"status": "OK"}

    engine = BacktestingEngine(strategy=PureContractStrategy())
    result = engine.run(loaded_dataset)
    assert result.strategy_name == "pure_contract"

def test_R17_strategy_cannot_access_infrastructure(loaded_dataset):
    """R17: Strategy cannot directly access DatasetStore, files, or P4.2 calendars."""
    strategy = IntrusiveStrategy()
    engine = BacktestingEngine(strategy=strategy)
    # Strategy should not find store/loader references in BacktestDataset context
    result = engine.run(loaded_dataset)
    assert result.strategy_name == "intrusive_strategy"

def test_R18_strategy_state_isolated_between_runs(loaded_dataset):
    """R18: Strategy state is properly initialized/isolated between independent backtest runs."""
    strategy = StatefulStrategy()
    engine = BacktestingEngine(strategy=strategy)

    res1 = engine.run(loaded_dataset)
    assert res1.metrics["run_count"] == 1
    assert res1.metrics["bars_processed"] == 2

    # Second run with same engine/strategy instance
    res2 = engine.run(loaded_dataset)
    # on_start resets or correctly handles isolated run lifecycle
    assert res2.metrics["bars_processed"] == 2
    assert strategy.run_count == 2
