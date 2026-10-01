import pytest
import pandas as pd
from src.execution_harness import TradeRecord
from src.performance_engine import PerformanceEngine, PerformanceInput, AllocationContract, ValuationBar, ContractViolationError

def test_tc_p4_01_exact_drawdown_magnitude():
    """TC-P4-01: Correctly calculates exact portfolio-equity peak, trough, and drawdown decimal magnitude."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-05", tz="UTC"), entry_price=100.0, exit_price=88.0, pnl=-12.0, exit_reason="STOP")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0), # Peak equity = 101,000
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=88.0)   # Trough equity = 98,800
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    expected_dd = (98800.0 / 101000.0) - 1.0
    assert abs(result.drawdown_series[-1].drawdown - expected_dd) < 1e-6

def test_tc_p4_02_new_peak_resets_duration():
    """TC-P4-02: New equity high resets current drawdown duration bars to 0."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-05", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=90.0),  # Drawdown
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=110.0)  # New peak reset
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.drawdown_series[-1].duration_bars == 0

def test_tc_p4_03_peak_to_trough_duration_bars():
    """TC-P4-03: Tracks exact peak-to-trough duration bars count on equity path."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-06", tz="UTC"), entry_price=100.0, exit_price=90.0, pnl=-10.0, exit_reason="STOP")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=120.0), # Peak (bar index 1)
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=110.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-06 00:00:00", tz="UTC"), close=90.0)   # Trough (bar index 3 -> 2 bars duration)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.metrics.max_drawdown_duration_bars == 2

def test_tc_p4_04_recovery_duration_tracking():
    """TC-P4-04: Records exact recovery bar duration and timestamp when equity returns to peak."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-06", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0), # Peak
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=99.0),  # Trough
        ValuationBar(timestamp=pd.Timestamp("2023-01-06 00:00:00", tz="UTC"), close=110.0)  # Recovery
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.drawdown_series[-1].drawdown == 0.0

def test_tc_p4_05_non_positive_capital_rejection():
    """TC-P4-05: Non-positive initial capital is rejected at constructor."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=100.0)
    bars = (ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),)
    with pytest.raises((ContractViolationError, ValueError)):
        PerformanceEngine(PerformanceInput(0.0, (), contract, bars))
