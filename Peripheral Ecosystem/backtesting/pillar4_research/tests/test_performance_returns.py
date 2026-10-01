import pytest
import pandas as pd
from src.execution_harness import TradeRecord
from src.performance_engine import PerformanceEngine, PerformanceInput, AllocationContract, ValuationBar

def test_tc_p3_01_severe_equity_erosion_boundary():
    """TC-P3-01: Severe drawdown with an active trade under positive closing price erodes equity precisely without bankruptcy."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=0.01, pnl=-99.99, exit_reason="STOP")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=0.01)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.terminal_state == "NORMAL"
    expected_equity = 90000.0 + (10000.0 / 100.0) * 0.01
    assert abs(result.equity_curve[-1].total_equity - expected_equity) < 1e-6
    assert result.equity_curve[-1].total_equity > 0.0

def test_tc_p3_02_utc_timestamp_alignment():
    """TC-P3-02: Return series strictly preserves UTC timezone-aware timestamp alignment."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=101.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=102.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars))
    result = engine.run()
    assert len(result.return_series) == len(bars) - 1
    assert result.return_series[0].timestamp.tzinfo is not None

def test_tc_p3_03_first_return_numerical_assertion():
    """TC-P3-03: First return calculation numerically matches E1/E0 - 1 with an active trade."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=105.0, pnl=5.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=105.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    e0 = 100000.0
    e1 = result.equity_curve[1].total_equity
    expected_return = (e1 / e0) - 1.0
    assert abs(result.return_series[0].return_val - expected_return) < 1e-6

def test_tc_p3_04_terminal_boundary_normal_state():
    """TC-P3-04: Normal terminal boundary states terminate with expected observation counts under valid v1.3 input."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=102.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=101.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars))
    result = engine.run()
    assert result.terminal_state == "NORMAL"
    assert len(result.return_series) == 2
