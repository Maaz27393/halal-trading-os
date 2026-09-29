from __future__ import annotations

import pytest
import pandas as pd
from src.calendar_adapter import load_and_verify_calendar, compute_canonical_hash
from src.dataset_store import DatasetStore
from src.dataset_loader import load_backtest_dataset
from src.backtest_dataset import BacktestDataset
from src.backtesting_engine import StrategyContract
from src.execution_harness import (
    ExecutionHarness,
    ExecutionConfig,
    TradeRecord,
    ExecutionHarnessError
)

class SignalOnFirstBarStrategy(StrategyContract):
    @property
    def name(self) -> str:
        return "signal_first_bar"

    def on_start(self, dataset: BacktestDataset) -> None:
        pass

    def on_bar(self, bar_index: int, row: pd.Series) -> dict:
        if bar_index == 0:
            return {
                "action": "BUY",
                "stop_loss": row["close"] * 0.98,
                "target": row["close"] * 1.05
            }
        return {"action": "HOLD"}

    def on_finish(self) -> dict:
        return {"status": "DONE"}

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
        'timestamp': pd.to_datetime([
            '2026-01-02 09:30:00', 
            '2026-01-02 09:31:00', 
            '2026-01-02 09:32:00'
        ], utc=True),
        'open': [100.0, 101.0, 102.0],
        'high': [101.5, 106.0, 103.0], # Bar 1 hits target (106.0 > target ~105)
        'low': [99.0, 100.5, 101.0],
        'close': [101.0, 102.0, 102.5],
        'volume': [1000, 1500, 1200]
    })
    res = temp_store.store(df, sample_calendar, symbol="AAPL", timeframe="1m")
    return load_backtest_dataset(temp_store, res.dataset_identity, sample_calendar)

def test_R19_deterministic_execution_results(loaded_dataset):
    """R19: Identical dataset + strategy + execution configuration produces deterministic execution results."""
    strategy1 = SignalOnFirstBarStrategy()
    strategy2 = SignalOnFirstBarStrategy()
    config = ExecutionConfig(slippage_pct=0.0, transaction_cost_pct=0.0)

    harness1 = ExecutionHarness(strategy=strategy1, config=config)
    harness2 = ExecutionHarness(strategy=strategy2, config=config)

    trades1 = harness1.run(loaded_dataset)
    trades2 = harness2.run(loaded_dataset)

    assert len(trades1) == len(trades2)
    assert trades1[0].entry_price == trades2[0].entry_price
    assert trades1[0].exit_price == trades2[0].exit_price
    assert trades1[0].exit_reason == trades2[0].exit_reason

def test_R20_harness_models_entry_position_exit_lifecycle(loaded_dataset):
    """R20: Execution harness correctly models entry -> position -> exit lifecycle."""
    strategy = SignalOnFirstBarStrategy()
    harness = ExecutionHarness(strategy=strategy)
    trades = harness.run(loaded_dataset)

    assert len(trades) == 1
    trade = trades[0]
    assert isinstance(trade, TradeRecord)
    assert trade.entry_timestamp is not None
    assert trade.exit_timestamp is not None
    assert trade.exit_reason in ["TARGET", "STOP", "STRATEGY_EXIT", "END_OF_DATA"]

def test_R21_stop_target_and_same_bar_policy(temp_store, sample_calendar):
    """R21: Stop-loss and target handling produce consistent deterministic outcomes with conservative same-bar policy."""
    # Create dataset where a single bar breaches both stop and target
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-02 09:30:00', '2026-01-02 09:31:00'], utc=True),
        'open': [100.0, 100.0],
        'high': [100.0, 110.0], # Breaches target (105)
        'low': [100.0, 90.0],   # Breaches stop (95)
        'close': [100.0, 100.0],
        'volume': [1000, 1000]
    })
    res = temp_store.store(df, sample_calendar, symbol="AAPL", timeframe="1m")
    dataset = load_backtest_dataset(temp_store, res.dataset_identity, sample_calendar)

    strategy = SignalOnFirstBarStrategy() # Enters at bar 0 (close=100), SL=98, Target=105
    harness = ExecutionHarness(strategy=strategy)
    trades = harness.run(dataset)

    assert len(trades) == 1
    # On bar 1, both high (110) and low (90) breach target and stop.
    # Conservative policy dictates STOP takes precedence.
    assert trades[0].exit_reason == "STOP"
    assert trades[0].exit_price == 98.0

def test_R22_no_live_execution_or_broker_dependency():
    """R22: Harness has no live execution/broker dependency and cannot dispatch real orders."""
    harness = ExecutionHarness(strategy=SignalOnFirstBarStrategy())
    
    # Assert absence of live broker attributes or dispatch methods
    forbidden_methods = ['connect_broker', 'send_order', 'place_live_order', 'authenticate_api']
    for meth in forbidden_methods:
        assert not hasattr(harness, meth), f"Forbidden live method '{meth}' found on ExecutionHarness!"
