import pytest
import pandas as pd
from src.execution_harness import TradeRecord
from src.performance_engine import PerformanceEngine, PerformanceInput, AllocationContract, ValuationBar

def test_tc_p2_01_flat_portfolio():
    """TC-P2-01: Equity curve remains flat at initial_capital when zero trades exist."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=100.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars))
    result = engine.run()
    assert all(pt.total_equity == 100000.0 for pt in result.equity_curve)

def test_tc_p2_02_profitable_single_trade():
    """TC-P2-02: Profitable trade increases cash and equity upon exit."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=120.0, pnl=20.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=120.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.equity_curve[-1].total_equity > 100000.0

def test_tc_p2_03_eod_certified_record_consumption():
    """TC-P2-03: Consumes certified END_OF_DATA TradeRecord without re-pricing from bar close."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=105.0, pnl=5.0, exit_reason="END_OF_DATA")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.terminal_state == "NORMAL"
    assert result.equity_curve[-1].valuation_state == "FLAT"
    expected_cash = 100000.0 - 10000.0 + (10000.0 / 100.0) * 105.0
    assert abs(result.equity_curve[-1].cash - expected_cash) < 1e-6

def test_tc_p2_04_entry_bar_close_valuation():
    """TC-P2-04: Entry bar uses explicit ValuationBar.close for mark-to-market valuation."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=100.0, pnl=0.0, exit_reason="TARGET")
    bars = (ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=98.0),)
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.equity_curve[0].valuation_state == "ACTIVE"
    assert abs(result.equity_curve[0].position_value - (10000.0 / 100.0) * 98.0) < 1e-6

def test_tc_p2_05_holding_bar_valuation():
    """TC-P2-05: Holding bars are valued at explicit ValuationBar.close."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-05", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=105.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-05 00:00:00", tz="UTC"), close=110.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.equity_curve[1].valuation_state == "ACTIVE"
    assert abs(result.equity_curve[1].position_value - (10000.0 / 100.0) * 105.0) < 1e-6

def test_tc_p2_06_equity_identity_invariant():
    """TC-P2-06: Equity = Cash + PositionValue holds precisely at all times."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    for pt in result.equity_curve:
        assert abs(pt.total_equity - (pt.cash + pt.position_value)) < 1e-6
