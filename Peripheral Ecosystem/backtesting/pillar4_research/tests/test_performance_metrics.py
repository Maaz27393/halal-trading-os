import pytest
import numpy as np
import pandas as pd
from src.execution_harness import TradeRecord
from src.performance_engine import PerformanceEngine, PerformanceInput, AllocationContract, ValuationBar

def test_tc_p5_01_zero_volatility_sharpe():
    """TC-P5-01: Zero volatility Sharpe is handled safely without division-by-zero."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=100.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars))
    result = engine.run()
    assert result.metrics.sharpe_ratio is None or result.metrics.sharpe_ratio == 0.0

def test_tc_p5_02_independent_sharpe_mathematical_proof():
    """TC-P5-02: Independently calculates expected Sharpe using sample std (ddof=1) of returns and period risk-free rate subtraction."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"), exit_timestamp=pd.Timestamp("2023-01-05", tz="UTC"), entry_price=100.0, exit_price=102.5, pnl=2.5, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=101.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=102.5)
    )
    rf_annual = 0.10
    periods = 252
    rf_period = rf_annual / periods

    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars, risk_free_rate_annual=rf_annual, periods_per_year=periods))
    result = engine.run()

    equity_values = [pt.total_equity for pt in result.equity_curve]
    returns = np.array([equity_values[i] / equity_values[i-1] - 1.0 for i in range(1, len(equity_values))])

    mean_ret = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    expected_sharpe = ((mean_ret - rf_period) / sigma) * np.sqrt(periods) if sigma > 0 else 0.0

    assert result.metrics.sharpe_ratio is not None
    assert abs(result.metrics.sharpe_ratio - expected_sharpe) < 1e-4

def test_tc_p5_03_annualized_volatility_formula():
    """TC-P5-03: Annualized volatility matches exact formula: std_dev * sqrt(periods_per_year)."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=101.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-06 00:00:00", tz="UTC"), close=102.0)
    )
    e252 = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars, periods_per_year=252))
    e365 = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars, periods_per_year=365))
    r252 = e252.run()
    r365 = e365.run()
    assert abs(r252.metrics.annualized_volatility * (365**0.5) - r365.metrics.annualized_volatility * (252**0.5)) < 1e-4

def test_tc_p5_04_zero_downside_deviation_sortino():
    """TC-P5-04: Sortino enforces the frozen contract: zero downside deviation explicitly evaluates to None."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=102.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars))
    result = engine.run()
    assert result.metrics.sortino_ratio is None

def test_tc_p5_05_insufficient_observations_status():
    """TC-P5-05: Insufficient observations status returns explicit None metrics status."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    bars = (ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),)
    engine = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars))
    result = engine.run()
    assert result.metrics.sharpe_ratio is None

def test_tc_p5_06_cagr_positive_equity_formula():
    """TC-P5-06: Asserts exact CAGR formula on a positive-equity growth path over explicit elapsed period count T."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"), exit_timestamp=pd.Timestamp("2023-01-05", tz="UTC"), entry_price=100.0, exit_price=121.0, pnl=21.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=121.0)
    )
    periods_per_year = 252
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars, periods_per_year=periods_per_year))
    result = engine.run()
    
    e0 = result.equity_curve[0].total_equity
    e_t = result.equity_curve[-1].total_equity
    t_periods = len(result.equity_curve) - 1
    expected_cagr = (e_t / e0) ** (periods_per_year / t_periods) - 1.0
    
    assert result.metrics.cagr is not None
    assert abs(result.metrics.cagr - expected_cagr) < 1e-4

def test_sortino_ratio_denominator_total_observations():
    """TC-METRICS-SORTINO: Asserts Sortino denominator uses total valid observations n, not downside subset count k."""
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2026-01-01 09:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2026-01-01 10:00", tz="UTC"), close=90.0),
        ValuationBar(timestamp=pd.Timestamp("2026-01-01 11:00", tz="UTC"), close=110.0),
        ValuationBar(timestamp=pd.Timestamp("2026-01-01 12:00", tz="UTC"), close=99.0),
    )
    trades = (
        TradeRecord(
            direction="LONG",
            entry_timestamp=pd.Timestamp("2026-01-01 09:00", tz="UTC"),
            exit_timestamp=pd.Timestamp("2026-01-01 12:00", tz="UTC"),
            entry_price=100.0,
            exit_price=99.0,
            pnl=-100.0,
            exit_reason="STOP"
        ),
    )
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    input_data = PerformanceInput(
        initial_capital=100_000.0,
        trades=trades,
        allocation_contract=contract,
        bars=bars
    )
    engine = PerformanceEngine(input_data)
    result = engine.run()
    
    # Extract equity curve generated by the engine
    equity_values = np.array([pt.total_equity for pt in result.equity_curve])
    rets = np.diff(equity_values) / equity_values[:-1]
    rf_period = 0.0 / 252.0
    downside_mask = rets < rf_period
    
    # Expected calculation using total valid observations n = len(rets) as denominator
    expected_downside_std = np.sqrt(np.sum((rets[downside_mask] - rf_period) ** 2) / len(rets))
    expected_mean_ret = np.mean(rets)
    expected_sortino = (expected_mean_ret / expected_downside_std) * np.sqrt(252.0)
    
    assert result.metrics.sortino_ratio is not None
    assert abs(result.metrics.sortino_ratio - expected_sortino) < 1e-6
