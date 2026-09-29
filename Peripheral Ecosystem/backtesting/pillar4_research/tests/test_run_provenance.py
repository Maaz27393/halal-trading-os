from __future__ import annotations

import pytest
import pandas as pd
from src.calendar_adapter import load_and_verify_calendar, compute_canonical_hash
from src.dataset_store import DatasetStore
from src.dataset_loader import load_backtest_dataset
from src.backtest_dataset import BacktestDataset
from src.backtesting_engine import StrategyContract
from src.execution_harness import ExecutionHarness, ExecutionConfig
from src.run_provenance import (
    BacktestRunManager,
    BacktestRunRecord,
    ExecutionConfigDTO,
    compute_run_identity
)

class VersionedDummyStrategy(StrategyContract):
    @property
    def name(self) -> str:
        return "versioned_dummy"

    @property
    def version(self) -> str:
        return "1.0.0"

    def on_start(self, dataset: BacktestDataset) -> None:
        pass

    def on_bar(self, bar_index: int, row: pd.Series) -> dict:
        if bar_index == 0:
            return {"action": "BUY", "stop_loss": row["close"] * 0.98, "target": row["close"] * 1.05}
        return {"action": "HOLD"}

    def on_finish(self) -> dict:
        return {"status": "OK"}

class ModifiedVersionStrategy(VersionedDummyStrategy):
    @property
    def version(self) -> str:
        return "1.1.0" # Different version/identity

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
        'high': [101.5, 106.0],
        'low': [99.0, 100.5],
        'close': [101.0, 102.0],
        'volume': [1000, 1500]
    })
    res = temp_store.store(df, sample_calendar, symbol="AAPL", timeframe="1m")
    return load_backtest_dataset(temp_store, res.dataset_identity, sample_calendar)

def test_R23_completed_run_records_full_provenance(loaded_dataset):
    """R23: A completed backtest run records dataset identity, calendar provenance, strategy ID/version, config, and engine/simulator versions."""
    strategy = VersionedDummyStrategy()
    config = ExecutionConfig(slippage_pct=0.001, transaction_cost_pct=0.002)
    manager = BacktestRunManager(strategy=strategy, config=config)

    record = manager.execute_run(loaded_dataset)

    assert isinstance(record, BacktestRunRecord)
    assert record.run_id is not None
    assert record.dataset_identity == loaded_dataset.dataset_identity
    assert record.dataset_sha256 == loaded_dataset.dataset_sha256
    assert record.calendar_sha256 == loaded_dataset.calendar_metadata.sha256
    assert record.strategy_id == "versioned_dummy"
    assert record.strategy_version == "1.0.0"
    assert record.execution_config.slippage_pct == 0.001
    assert record.engine_version is not None
    assert record.simulator_version is not None
    assert isinstance(record.trade_records, list)

def test_R24_changing_strategy_or_config_produces_distinct_run_identity(loaded_dataset):
    """R24: Changing strategy identity, version, or configuration produces a distinct run identity without collision."""
    strat_v1 = VersionedDummyStrategy()
    strat_v2 = ModifiedVersionStrategy()
    
    config_a = ExecutionConfig(slippage_pct=0.0)
    config_b = ExecutionConfig(slippage_pct=0.005)

    manager_a = BacktestRunManager(strategy=strat_v1, config=config_a)
    manager_b = BacktestRunManager(strategy=strat_v2, config=config_a)
    manager_c = BacktestRunManager(strategy=strat_v1, config=config_b)

    rec_a = manager_a.execute_run(loaded_dataset)
    rec_b = manager_b.execute_run(loaded_dataset)
    rec_c = manager_c.execute_run(loaded_dataset)

    # Ensure run IDs are completely unique and non-colliding
    assert rec_a.run_id != rec_b.run_id
    assert rec_a.run_id != rec_c.run_id
    assert rec_b.run_id != rec_c.run_id
