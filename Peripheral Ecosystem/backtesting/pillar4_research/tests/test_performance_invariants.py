import pytest
import pandas as pd
from src.execution_harness import TradeRecord
from src.performance_engine import PerformanceEngine, PerformanceInput, AllocationContract, ValuationBar, ContractViolationError

def test_tc_p6_01_traderecord_complete_field_snapshot():
    """TC-P6-01: Captures all TradeRecord fields before and after run, verifying absolute immutability and frozen assignment rejection."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(
        entry_time=pd.Timestamp("2023-01-03", tz="UTC"),
        exit_time=pd.Timestamp("2023-01-04", tz="UTC"),
        entry_price=100.0,
        exit_price=110.0,
        pnl=10.0,
        exit_reason="TARGET"
    )
    fields_before = {
        "entry_time": trade.entry_time,
        "exit_time": trade.exit_time,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "pnl": trade.pnl,
        "exit_reason": trade.exit_reason
    }
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    engine.run()
    
    fields_after = {
        "entry_time": trade.entry_time,
        "exit_time": trade.exit_time,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "pnl": trade.pnl,
        "exit_reason": trade.exit_reason
    }
    assert fields_before == fields_after
    
    with pytest.raises(Exception):
        trade.exit_price = 999.0

def test_tc_p6_02_friction_isolation():
    """TC-P6-02: B4.9 derives economics solely from certified TradeRecords without external friction config."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    result = engine.run()
    assert result.equity_curve[-1].total_equity > 100000.0

def test_tc_p6_03_execution_isolation():
    """TC-P6-03: Performance layer does not modify execution semantics or exit reasons."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(entry_time=pd.Timestamp("2023-01-03", tz="UTC"), exit_time=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
    bars = (
        ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),
        ValuationBar(timestamp=pd.Timestamp("2023-01-04 00:00:00", tz="UTC"), close=110.0)
    )
    engine = PerformanceEngine(PerformanceInput(100000.0, (trade,), contract, bars))
    engine.run()
    assert trade.exit_reason == "TARGET"

def test_tc_p6_04_network_isolation_boundary(monkeypatch):
    """TC-P6-04: Monkeypatches socket.socket to fail loudly if network access is attempted during performance execution."""
    import socket
    def mock_socket(*args, **kwargs):
        raise RuntimeError("Network access forbidden during performance execution")
    monkeypatch.setattr(socket, "socket", mock_socket)
    
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    bars = (ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00", tz="UTC"), close=100.0),)
    engine = PerformanceEngine(PerformanceInput(100000.0, (), contract, bars))
    result = engine.run()
    assert result.terminal_state == "NORMAL"

def test_tc_p6_05_fail_closed_on_empty_dataset_bars():
    """TC-P6-05: Fails closed when dataset bars tuple is empty."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    with pytest.raises((ContractViolationError, ValueError)):
        PerformanceEngine(PerformanceInput(100000.0, (), contract, ()))

def test_tc_p6_06_fail_closed_on_naive_timestamps():
    """TC-P6-06: Fails closed when ValuationBar timestamps are timezone-naive."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    naive_bar = ValuationBar(timestamp=pd.Timestamp("2023-01-03 00:00:00"), close=100.0)
    with pytest.raises((ContractViolationError, ValueError, TypeError)):
        PerformanceEngine(PerformanceInput(100000.0, (), contract, (naive_bar,)))
