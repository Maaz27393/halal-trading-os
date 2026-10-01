import pytest
import pandas as pd
from src.execution_harness import TradeRecord
from src.performance_engine import PerformanceEngine, PerformanceInput, AllocationContract, ValuationBar, ContractViolationError

def test_tc_p6_01_traderecord_complete_field_snapshot():
    """TC-P6-01: Captures all TradeRecord fields before and after run, verifying absolute immutability and frozen assignment rejection."""
    contract = AllocationContract(sizing_mode="FIXED_CAPITAL", allocation_value=10000.0)
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"),
        exit_timestamp=pd.Timestamp("2023-01-04", tz="UTC"),
        entry_price=100.0,
        exit_price=110.0,
        pnl=10.0,
        exit_reason="TARGET"
    )
    fields_before = {
        "entry_time": trade.entry_timestamp,
        "exit_time": trade.exit_timestamp,
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
        "entry_time": trade.entry_timestamp,
        "exit_time": trade.exit_timestamp,
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
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"), exit_timestamp=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
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
    trade = TradeRecord(direction="LONG", entry_timestamp=pd.Timestamp("2023-01-03", tz="UTC"), exit_timestamp=pd.Timestamp("2023-01-04", tz="UTC"), entry_price=100.0, exit_price=110.0, pnl=10.0, exit_reason="TARGET")
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

def test_rejects_non_utc_timezone_aware_timestamp():
    bars = (
        ValuationBar(
            timestamp=pd.Timestamp("2026-01-01 09:15", tz="Asia/Kolkata"),
            close=100.0,
        ),
        ValuationBar(
            timestamp=pd.Timestamp("2026-01-01 09:16", tz="Asia/Kolkata"),
            close=101.0,
        ),
    )
    input_data = PerformanceInput(
        initial_capital=100_000.0,
        trades=(),
        allocation_contract=AllocationContract(
            sizing_mode="FIXED_CAPITAL",
            allocation_value=10_000.0,
        ),
        bars=bars,
    )
    with pytest.raises(ContractViolationError):
        PerformanceEngine(input_data)

def test_rejects_duplicate_valuation_timestamps():
    ts = pd.Timestamp("2026-01-01 09:15", tz="UTC")
    bars = (
        ValuationBar(timestamp=ts, close=100.0),
        ValuationBar(timestamp=ts, close=101.0),
    )
    input_data = PerformanceInput(
        initial_capital=100_000.0,
        trades=(),
        allocation_contract=AllocationContract(
            sizing_mode="FIXED_CAPITAL",
            allocation_value=10_000.0,
        ),
        bars=bars,
    )
    with pytest.raises(ContractViolationError):
        PerformanceEngine(input_data)

def test_rejects_non_monotonic_valuation_timestamps():
    bars = (
        ValuationBar(
            timestamp=pd.Timestamp("2026-01-01 09:16", tz="UTC"),
            close=100.0,
        ),
        ValuationBar(
            timestamp=pd.Timestamp("2026-01-01 09:15", tz="UTC"),
            close=101.0,
        ),
    )
    input_data = PerformanceInput(
        initial_capital=100_000.0,
        trades=(),
        allocation_contract=AllocationContract(
            sizing_mode="FIXED_CAPITAL",
            allocation_value=10_000.0,
        ),
        bars=bars,
    )
    with pytest.raises(ContractViolationError):
        PerformanceEngine(input_data)

@pytest.mark.parametrize("close", [float("nan"), float("inf"), float("-inf")])
def test_rejects_non_finite_valuation_close(close):
    bars = (
        ValuationBar(
            timestamp=pd.Timestamp("2026-01-01 09:15", tz="UTC"),
            close=close,
        ),
    )
    input_data = PerformanceInput(
        initial_capital=100_000.0,
        trades=(),
        allocation_contract=AllocationContract(
            sizing_mode="FIXED_CAPITAL",
            allocation_value=10_000.0,
        ),
        bars=bars,
    )
    with pytest.raises(ContractViolationError):
        PerformanceEngine(input_data)

@pytest.mark.parametrize("allocation", [0.0, -1.0])
def test_rejects_non_positive_fixed_capital_allocation(allocation):
    bars = (
        ValuationBar(
            timestamp=pd.Timestamp("2026-01-01 09:15", tz="UTC"),
            close=100.0,
        ),
    )
    input_data = PerformanceInput(
        initial_capital=100_000.0,
        trades=(),
        allocation_contract=AllocationContract(
            sizing_mode="FIXED_CAPITAL",
            allocation_value=allocation,
        ),
        bars=bars,
    )
    with pytest.raises(ContractViolationError):
        PerformanceEngine(input_data).run()
