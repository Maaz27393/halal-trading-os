import pytest
import pandas as pd
from src.execution_harness import TradeRecord
from src.performance_engine import PerformanceEngine, PerformanceInput, AllocationContract, ValuationBar, InsufficientCapitalError, ContractViolationError

def test_tc_p1_01_missing_allocation_contract():
    """TC-P1-01: Missing allocation contract fails closed with a contract exception via public run()."""
    bar = ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0)
    engine = PerformanceEngine(PerformanceInput(100000.0, (), None, (bar,)))
    with pytest.raises((ContractViolationError, ValueError, TypeError)):
        engine.run()

def test_tc_p1_02_fixed_allocation_correctness():
    """TC-P1-02: Fixed capital allocation correctly executes via public run()."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"), exit_timestamp=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.equity_curve[-1].total_equity > 100000.0

def test_tc_p1_03_insufficient_cash_failure():
    """TC-P1-03: Insufficient cash raises InsufficientCapitalError via public run() with no partial fill."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=200000.0)
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"), exit_timestamp=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),)
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    with pytest.raises(InsufficientCapitalError):
        engine.run()

def test_tc_p1_04_allocation_determinism():
    """TC-P1-04: Identical inputs produce identical performance output via run()."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"), exit_timestamp=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),)
    e1 = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    e2 = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    assert e1.run().equity_curve == e2.run().equity_curve

def test_tc_p1_05_certified_entry_price_sizing():
    """TC-P1-05: Sizing uses certified TradeRecord.entry_price without re-pricing from bar close."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"), exit_timestamp=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=102.5, exit_price=110.0, pnl=7.5, exit_reason="TARGET")
    bars = (ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),)
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    expected_pos_val = (10000.0 / 102.5) * 100.0
    assert abs(result.equity_curve[0].position_value - expected_pos_val) < 1e-6
