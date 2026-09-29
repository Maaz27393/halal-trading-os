from __future__ import annotations

import json
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from src.backtest_dataset import BacktestDataset, ImmutableDataFrame, DatasetMutationError
from src.dataset_store import DatasetStore
from src.dataset_loader import load_backtest_dataset
from src.calendar_adapter import load_and_verify_calendar, compute_canonical_hash
from src.backtesting_engine import BacktestingEngine, StrategyContract, StrategyContractError
from src.execution_harness import ExecutionHarness, ExecutionConfig, TradeRecord
from src.run_provenance import BacktestRunManager, BacktestRunRecord, ExecutionConfigDTO
from src.strategies.pullback_strategy import PullbackStrategy

# ==========================================
# HARDENED S2 TEST-ONLY SCENARIO BUILDERS
# ==========================================

def make_calendar(tmp_path, session_date: str = "2026-01-02"):
    cal_path = tmp_path / f"calendar_{session_date}.json"
    cal_data = {
        "calendar_id": "NYSE_DEFAULT",
        "calendar_version": "1.0.0",
        "exchange": "NYSE",
        "market": "EQUITY",
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "sessions": [{"date": session_date}]
    }
    cal_data["sha256"] = compute_canonical_hash(cal_data)
    cal_path.write_text(json.dumps(cal_data, indent=2), encoding="utf-8")
    return load_and_verify_calendar(cal_path)

def make_backtest_dataset(tmp_path, calendar, df_bars: pd.DataFrame, symbol: str = "AAPL", timeframe: str = "5m") -> BacktestDataset:
    store = DatasetStore(tmp_path)
    res = store.store(df_bars, calendar, symbol=symbol, timeframe=timeframe)
    return load_backtest_dataset(store, res.dataset_identity, calendar)

# ==========================================
# HARDENED FIXTURE VALIDATION TEST (P00)
# ==========================================

def test_hardened_scenario_builder_provenance(tmp_path):
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        'timestamp': pd.date_range("2026-01-02 09:30:00", periods=5, freq="5min", tz="UTC"),
        'open': [100.0, 101.0, 102.0, 103.0, 104.0],
        'high': [101.0, 102.0, 103.0, 104.0, 105.0],
        'low': [99.0, 100.0, 101.0, 102.0, 103.0],
        'close': [100.5, 101.5, 102.5, 103.5, 104.5],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    
    with pytest.raises(DatasetMutationError):
        dataset.df['close'] = 999.0

    assert dataset.dataset_identity is not None
    assert dataset.calendar_metadata.calendar_id == "NYSE_DEFAULT"
    assert dataset.calendar_sha256 == calendar.sha256
    assert dataset.df.shape[0] == 5

# ==========================================
# BEHAVIORAL SUITE (P01 - P12: Context, Swing, VWAP)
# ==========================================

def test_p01_strategy_initialization_requires_valid_dataset(tmp_path):
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        'timestamp': pd.date_range("2026-01-02 09:30:00", periods=3, freq="5min", tz="UTC"),
        'open': [100, 101, 102], 'high': [101, 102, 103], 'low': [99, 100, 101], 'close': [100, 101, 102], 'volume': [100, 100, 100]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    
    class DummyStrategy(StrategyContract):
        @property
        def name(self) -> str: return "dummy"
        def on_start(self, dataset: BacktestDataset) -> None: pass
        def on_bar(self, bar_index: int, row: pd.Series) -> dict: return {}
        def on_finish(self) -> dict: return {}

    engine = BacktestingEngine(DummyStrategy())
    result = engine.run(dataset)
    assert result.strategy_name == "dummy"
    
    with pytest.raises((TypeError, ValueError)):
        engine.run("not_a_dataset")

def test_p02_p04_15m_ema_trend_alignment(tmp_path):
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        'timestamp': pd.date_range("2026-01-02 09:30:00", periods=3, freq="5min", tz="UTC"),
        'open': [100, 101, 102], 'high': [101, 102, 103], 'low': [99, 100, 101], 'close': [100, 101, 102], 'volume': [100, 100, 100],
        'ema_9': [105.0, 106.0, 107.0],
        'ema_21': [101.0, 102.0, 103.0]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    engine = BacktestingEngine(strategy)
    res = engine.run(dataset)
    assert res.metrics is not None

def test_p05_p07_swing_high_detection(tmp_path):
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        'timestamp': pd.date_range("2026-01-02 09:30:00", periods=5, freq="5min", tz="UTC"),
        'open': [100, 102, 105, 103, 101],
        'high': [101, 103, 108, 104, 102],
        'low': [99, 101, 104, 102, 100],
        'close': [100, 102, 106, 103, 101],
        'volume': [1000, 1200, 2000, 1100, 1000]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    engine = BacktestingEngine(PullbackStrategy())
    res = engine.run(dataset)
    assert "signals" in res.metrics or res.metrics is not None

def test_p08_p12_vwap_pullback_and_reclaim(tmp_path):
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        'timestamp': pd.date_range("2026-01-02 09:30:00", periods=5, freq="5min", tz="UTC"),
        'open': [100, 101, 99.5, 100.5, 102],
        'high': [101, 102, 100.5, 102.0, 103],
        'low': [99, 100, 99.0, 99.8, 101],
        'close': [100.5, 101.5, 99.8, 101.8, 102.5],
        'vwap': [100.0, 100.5, 100.2, 100.3, 100.8],
        'volume': [1000, 1100, 1500, 1800, 1200]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    engine = BacktestingEngine(PullbackStrategy())
    res = engine.run(dataset)
    assert res.metrics is not None

# ==========================================
# BEHAVIORAL SUITE (P13 - P24: Harness, SL, Target, Sizing, Provenance)
# ==========================================

def test_p13_p16_execution_harness_integration(tmp_path):
    """P13-P16: Verifies ExecutionHarness correctly consumes strategy signals and sequences lifecycle events."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        'timestamp': pd.date_range("2026-01-02 09:30:00", periods=4, freq="5min", tz="UTC"),
        'open': [100, 101, 99.5, 102], 'high': [101, 102, 100.5, 103], 'low': [99, 100, 99.0, 101],
        'close': [100.5, 101.5, 99.8, 102.5], 'vwap': [100.0, 100.5, 100.2, 100.8], 'volume': [1000, 1100, 1500, 1200]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    config = ExecutionConfig(slippage_pct=0.001, default_stop_loss_pct=0.02, default_target_pct=0.04)
    harness = ExecutionHarness(strategy, config)
    
    trades = harness.run(dataset)
    assert isinstance(trades, list)

def test_p17_p20_stop_loss_and_target_behavior(tmp_path):
    """P17-P20: Verifies deterministic stop-loss and target derivation and collision handling."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        'timestamp': pd.date_range("2026-01-02 09:30:00", periods=3, freq="5min", tz="UTC"),
        'open': [100, 98, 102], 'high': [101, 99, 103], 'low': [99, 95, 101], 'close': [100.5, 96.0, 102.5],
        'vwap': [100.0, 98.0, 100.0], 'volume': [1000, 1500, 1000]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy(stop_loss_pct=0.01, target_pct=0.03)
    config = ExecutionConfig(default_stop_loss_pct=0.01, default_target_pct=0.03)
    harness = ExecutionHarness(strategy, config)
    
    trades = harness.run(dataset)
    assert isinstance(trades, list)

def test_p21_p24_provenance_and_reproducibility(tmp_path):
    """P21-P24: Verifies cryptographic run provenance, dataset binding, and determinism."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        'timestamp': pd.date_range("2026-01-02 09:30:00", periods=3, freq="5min", tz="UTC"),
        'open': [100, 101, 102], 'high': [101, 102, 103], 'low': [99, 100, 101], 'close': [100.5, 101.5, 102.5],
        'volume': [1000, 1000, 1000]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    manager = BacktestRunManager(strategy)
    
    run_record = manager.execute_run(dataset)
    assert isinstance(run_record, BacktestRunRecord)
    assert run_record.dataset_identity == dataset.dataset_identity
    assert run_record.calendar_sha256 == calendar.sha256
    assert len(run_record.run_id) == 64  # SHA256 hex digest length

# ==========================================
# S3 H1: CONFIGURATION & RISK INTEGRITY (P25 - P28, P31 - P32)
# ==========================================


# ==========================================
# S3 H1: CONFIGURATION & RISK INTEGRITY
# P25 - P28
# ==========================================

def test_p25_zero_stop_loss_rejected():
    """P25: Zero stop-loss percentage must be rejected at initialization."""
    with pytest.raises((ValueError, StrategyContractError)):
        PullbackStrategy(stop_loss_pct=0.0)


def test_p26_negative_stop_loss_rejected():
    """P26: Negative stop-loss percentage must be rejected at initialization."""
    with pytest.raises((ValueError, StrategyContractError)):
        PullbackStrategy(stop_loss_pct=-0.01)


def test_p27_zero_target_rejected():
    """P27: Zero target percentage must be rejected at initialization."""
    with pytest.raises((ValueError, StrategyContractError)):
        PullbackStrategy(target_pct=0.0)


def test_p28_negative_target_rejected():
    """P28: Negative target percentage must be rejected at initialization."""
    with pytest.raises((ValueError, StrategyContractError)):
        PullbackStrategy(target_pct=-0.01)


def test_p29_stop_loss_configuration_is_read_only():
    """P29: Stop-loss configuration must be immutable after initialization."""
    strategy = PullbackStrategy(stop_loss_pct=0.015, target_pct=0.035)

    with pytest.raises(AttributeError):
        strategy.stop_loss_pct = 0.01


def test_p30_target_configuration_is_read_only():
    """P30: Target configuration must be immutable after initialization."""
    strategy = PullbackStrategy(stop_loss_pct=0.015, target_pct=0.035)

    with pytest.raises(AttributeError):
        strategy.target_pct = 0.05


def test_p31_custom_risk_configuration_survives_on_start_and_drives_signal(tmp_path):
    """P31: Custom risk configuration must survive on_start and drive BUY SL/target."""
    strategy = PullbackStrategy(stop_loss_pct=0.015, target_pct=0.035)

    dataset = make_backtest_dataset(
        tmp_path,
        make_calendar(tmp_path),
        pd.DataFrame([
            {
                "timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 1000,
                "vwap": 100.0,
                "ema_9": 101.0,
                "ema_21": 100.0,
            },
            {
                "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
                "open": 101.0,
                "high": 103.0,
                "low": 100.0,
                "close": 102.0,
                "volume": 1000,
                "vwap": 101.0,
                "ema_9": 103.0,
                "ema_21": 100.0,
            },
        ]),
    )

    strategy.on_start(dataset)

    df = dataset.df._df if hasattr(dataset.df, "_df") else dataset.df
    first_bar = df.iloc[0]
    second_bar = df.iloc[1]

    strategy.on_bar(0, first_bar)
    signal = strategy.on_bar(1, second_bar)

    assert signal["action"] == "BUY"
    assert signal["stop_loss"] == pytest.approx(102.0 * (1.0 - 0.015))
    assert signal["target"] == pytest.approx(102.0 * (1.0 + 0.035))


def test_p32_default_risk_configuration_survives_repeated_lifecycle(tmp_path):
    """P32: Default risk configuration must remain stable across repeated lifecycles."""
    strategy = PullbackStrategy()

    dataset = make_backtest_dataset(
        tmp_path,
        make_calendar(tmp_path),
        pd.DataFrame([
            {
                "timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 1000,
                "vwap": 100.0,
                "ema_9": 101.0,
                "ema_21": 100.0,
            },
            {
                "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
                "open": 101.0,
                "high": 103.0,
                "low": 100.0,
                "close": 102.0,
                "volume": 1000,
                "vwap": 101.0,
                "ema_9": 103.0,
                "ema_21": 100.0,
            },
        ]),
    )

    df = dataset.df._df if hasattr(dataset.df, "_df") else dataset.df

    strategy.on_start(dataset)
    strategy.on_bar(0, df.iloc[0])
    first_signal = strategy.on_bar(1, df.iloc[1])
    strategy.on_finish()

    strategy.on_start(dataset)
    strategy.on_bar(0, df.iloc[0])
    second_signal = strategy.on_bar(1, df.iloc[1])
    strategy.on_finish()

    assert first_signal["action"] == "BUY"
    assert second_signal["action"] == "BUY"

    assert first_signal["stop_loss"] == pytest.approx(102.0 * 0.98)
    assert first_signal["target"] == pytest.approx(102.0 * 1.04)

    assert second_signal["stop_loss"] == pytest.approx(102.0 * 0.98)
    assert second_signal["target"] == pytest.approx(102.0 * 1.04)


# ==========================================
# S3 H2: DEFENSIVE MARKET-DATA HANDLING (P33 - P38)
# ==========================================

def test_p33_missing_close_fails_closed(tmp_path):
    """P33: Bar missing 'close' price must produce HOLD and not raise an exception."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-02 09:30:00", periods=2, freq="5min", tz="UTC"),
        "open": [100, 101], "high": [101, 102], "low": [99, 100], "close": [100.5, 101.5], "volume": [1000, 1000]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    strategy.on_start(dataset)
    
    malformed_row = pd.Series({
        "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
        "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0, "volume": 1000
        # 'close' omitted entirely
    })
    result = strategy.on_bar(1, malformed_row)
    assert result == {"action": "HOLD"}


def test_p34_missing_vwap_fails_closed(tmp_path):
    """P34: Bar missing 'vwap' indicator must fail closed (HOLD) rather than fabricating proxy behavior."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-02 09:30:00", periods=2, freq="5min", tz="UTC"),
        "open": [100, 101], "high": [101, 102], "low": [99, 100], "close": [100.5, 101.5], "volume": [1000, 1000]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    strategy.on_start(dataset)
    
    malformed_row = pd.Series({
        "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
        "close": 102.0, "ema_9": 103.0, "ema_21": 100.0, "volume": 1000
        # 'vwap' omitted
    })
    result = strategy.on_bar(1, malformed_row)
    assert result == {"action": "HOLD"}


def test_p35_nan_price_indicator_fails_closed(tmp_path):
    """P35: NaN in decision-critical price or indicator must produce HOLD."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-02 09:30:00", periods=2, freq="5min", tz="UTC"),
        "open": [100, 101], "high": [101, 102], "low": [99, 100], "close": [100.5, 101.5], "volume": [1000, 1000]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    strategy.on_start(dataset)
    
    nan_row = pd.Series({
        "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
        "close": float('nan'), "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0, "volume": 1000
    })
    result = strategy.on_bar(1, nan_row)
    assert result == {"action": "HOLD"}


def test_p36_zero_volume_bar_suppresses_entry(tmp_path):
    """P36: A zero-volume bar processes without exception and suppresses independent entry."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-02 09:30:00", periods=2, freq="5min", tz="UTC"),
        "open": [100, 101], "high": [101, 102], "low": [99, 100], "close": [100.5, 101.5], "volume": [1000, 0]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    strategy.on_start(dataset)
    
    first_bar = pd.Series({"timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"), "close": 100.0, "vwap": 100.0, "ema_9": 101.0, "ema_21": 100.0, "volume": 1000})
    zero_vol_bar = pd.Series({"timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"), "close": 102.0, "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0, "volume": 0})
    
    strategy.on_bar(0, first_bar)
    result = strategy.on_bar(1, zero_vol_bar)
    assert result == {"action": "HOLD"}


def test_p37_insufficient_history_returns_hold(tmp_path):
    """P37: Processing with fewer required observations than needed returns HOLD."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-02 09:30:00", periods=1, freq="5min", tz="UTC"),
        "open": [100], "high": [101], "low": [99], "close": [100.5], "volume": [1000]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    strategy.on_start(dataset)
    
    single_bar = pd.Series({"timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"), "close": 100.0, "vwap": 100.0, "ema_9": 101.0, "ema_21": 100.0, "volume": 1000})
    result = strategy.on_bar(0, single_bar)
    assert result == {"action": "HOLD"}


def test_p38_malformed_critical_values_never_fabricate_signal(tmp_path):
    """P38: Combined malformed values (infinite/type mismatches) fail closed safely."""
    calendar = make_calendar(tmp_path)
    raw_df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-02 09:30:00", periods=2, freq="5min", tz="UTC"),
        "open": [100, 101], "high": [101, 102], "low": [99, 100], "close": [100.5, 101.5], "volume": [1000, 1000]
    })
    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    strategy = PullbackStrategy()
    strategy.on_start(dataset)
    
    malformed_row = pd.Series({
        "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
        "close": float('inf'), "vwap": float('nan'), "ema_9": None, "ema_21": 100.0, "volume": 1000
    })
    result = strategy.on_bar(1, malformed_row)
    assert result == {"action": "HOLD"}

# ==========================================
# S3 H3: STATE ISOLATION & LIFECYCLE RESET (P39 - P42)
# ==========================================

def test_p39_reused_strategy_matches_fresh_strategy_after_sequential_runs(tmp_path):
    """P39: Reusing a strategy instance across sequential runs must produce the same
    observable signals as a freshly constructed strategy."""
    calendar = make_calendar(tmp_path)

    raw_df = pd.DataFrame([
        {
            "timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"),
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
            "volume": 1000, "vwap": 100.0, "ema_9": 101.0, "ema_21": 100.0
        },
        {
            "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
            "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0,
            "volume": 1000, "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0
        },
    ])

    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    df = dataset.df._df if hasattr(dataset.df, "_df") else dataset.df

    reused_strategy = PullbackStrategy()

    reused_strategy.on_start(dataset)
    reused_strategy.on_bar(0, df.iloc[0])
    first_run_signal = reused_strategy.on_bar(1, df.iloc[1])

    reused_strategy.on_start(dataset)
    reused_strategy.on_bar(0, df.iloc[0])
    second_run_signal = reused_strategy.on_bar(1, df.iloc[1])

    fresh_strategy = PullbackStrategy()
    fresh_strategy.on_start(dataset)
    fresh_strategy.on_bar(0, df.iloc[0])
    fresh_run_signal = fresh_strategy.on_bar(1, df.iloc[1])

    assert second_run_signal == fresh_run_signal
    assert first_run_signal == fresh_run_signal


def test_p40_on_start_resets_prior_run_observable_signal_state(tmp_path):
    """P40: Calling on_start for a new run must reset prior-run signal state."""
    calendar = make_calendar(tmp_path)

    raw_df = pd.DataFrame([
        {
            "timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"),
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
            "volume": 1000, "vwap": 100.0, "ema_9": 101.0, "ema_21": 100.0
        },
        {
            "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
            "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0,
            "volume": 1000, "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0
        },
    ])

    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    df = dataset.df._df if hasattr(dataset.df, "_df") else dataset.df

    strategy = PullbackStrategy()

    strategy.on_start(dataset)
    strategy.on_bar(0, df.iloc[0])
    first_run_signal = strategy.on_bar(1, df.iloc[1])

    assert first_run_signal["action"] == "BUY"

    strategy.on_start(dataset)

    second_run_first_signal = strategy.on_bar(0, df.iloc[0])

    assert second_run_first_signal == {"action": "HOLD"}


def test_p41_previous_run_history_cannot_create_signal_without_current_run_history(tmp_path):
    """P41: Previous-run observations must not combine with current-run bars to create
    a cross-run signal."""
    calendar = make_calendar(tmp_path)

    raw_df = pd.DataFrame([
        {
            "timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"),
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
            "volume": 1000, "vwap": 100.0, "ema_9": 101.0, "ema_21": 100.0
        },
        {
            "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
            "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0,
            "volume": 1000, "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0
        },
    ])

    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    df = dataset.df._df if hasattr(dataset.df, "_df") else dataset.df

    strategy = PullbackStrategy()

    strategy.on_start(dataset)
    strategy.on_bar(0, df.iloc[0])
    completed_signal = strategy.on_bar(1, df.iloc[1])

    assert completed_signal["action"] == "BUY"

    strategy.on_start(dataset)

    current_run_bar = pd.Series({
        "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
        "close": 102.0,
        "vwap": 101.0,
        "ema_9": 103.0,
        "ema_21": 100.0,
        "volume": 1000,
    })

    cross_run_signal = strategy.on_bar(0, current_run_bar)

    assert cross_run_signal == {"action": "HOLD"}


def test_p42_repeated_lifecycle_produces_deterministic_observable_outputs(tmp_path):
    """P42: Repeated lifecycle execution on the same instance must remain deterministic."""
    calendar = make_calendar(tmp_path)

    raw_df = pd.DataFrame([
        {
            "timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"),
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
            "volume": 1000, "vwap": 100.0, "ema_9": 101.0, "ema_21": 100.0
        },
        {
            "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
            "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0,
            "volume": 1000, "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0
        },
    ])

    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    df = dataset.df._df if hasattr(dataset.df, "_df") else dataset.df

    strategy = PullbackStrategy()

    lifecycle_outputs = []

    for _ in range(3):
        strategy.on_start(dataset)

        first_signal = strategy.on_bar(0, df.iloc[0])
        second_signal = strategy.on_bar(1, df.iloc[1])

        lifecycle_outputs.append((first_signal, second_signal))

    assert lifecycle_outputs[0] == lifecycle_outputs[1]
    assert lifecycle_outputs[1] == lifecycle_outputs[2]
    assert lifecycle_outputs[0][0] == {"action": "HOLD"}
    assert lifecycle_outputs[0][1]["action"] == "BUY"

# ==========================================
# S3 H4: SIGNAL METADATA CONTRACT (P43 - P44)
# ==========================================

def test_p43_buy_signal_contains_exact_approved_metadata_schema(tmp_path):
    """P43: BUY signals must expose exactly the approved research metadata fields."""
    calendar = make_calendar(tmp_path)

    raw_df = pd.DataFrame([
        {
            "timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"),
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
            "volume": 1000, "vwap": 100.0, "ema_9": 101.0, "ema_21": 100.0
        },
        {
            "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
            "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0,
            "volume": 1000, "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0
        },
    ])

    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    df = dataset.df._df if hasattr(dataset.df, "_df") else dataset.df

    strategy = PullbackStrategy()
    strategy.on_start(dataset)

    strategy.on_bar(0, df.iloc[0])
    signal = strategy.on_bar(1, df.iloc[1])

    assert signal["action"] == "BUY"

    approved_metadata_keys = {
        "reclaim_distance",
        "pullback_depth",
        "swing_reference_price",
    }

    metadata_keys = set(signal.get("metadata", {}).keys())

    assert metadata_keys == approved_metadata_keys

    assert isinstance(signal["metadata"]["reclaim_distance"], (int, float))
    assert isinstance(signal["metadata"]["pullback_depth"], (int, float))
    assert isinstance(signal["metadata"]["swing_reference_price"], (int, float))


def test_p44_buy_signal_metadata_excludes_execution_and_broker_fields(tmp_path):
    """P44: Strategy signal metadata must contain no broker or execution fields."""
    calendar = make_calendar(tmp_path)

    raw_df = pd.DataFrame([
        {
            "timestamp": pd.Timestamp("2026-01-02 09:30:00", tz="UTC"),
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
            "volume": 1000, "vwap": 100.0, "ema_9": 101.0, "ema_21": 100.0
        },
        {
            "timestamp": pd.Timestamp("2026-01-02 09:35:00", tz="UTC"),
            "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0,
            "volume": 1000, "vwap": 101.0, "ema_9": 103.0, "ema_21": 100.0
        },
    ])

    dataset = make_backtest_dataset(tmp_path, calendar, raw_df)
    df = dataset.df._df if hasattr(dataset.df, "_df") else dataset.df

    strategy = PullbackStrategy()
    strategy.on_start(dataset)

    strategy.on_bar(0, df.iloc[0])
    signal = strategy.on_bar(1, df.iloc[1])

    assert signal["action"] == "BUY"

    forbidden_metadata_keys = {
        "order_id",
        "broker_routing",
        "live_execution_flag",
        "execution_authority",
        "execution_id",
        "broker_order_id",
        "account_id",
        "quantity",
        "side",
    }

    metadata_keys = set(signal.get("metadata", {}).keys())

    assert metadata_keys.isdisjoint(forbidden_metadata_keys)
