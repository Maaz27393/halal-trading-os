import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from execution_state_machine import ExecutionOrder, OrderState
from position_state_engine import PositionStateEngine
from execution_reconciliation import ExecutionReconciler

def run_phase9e_tests():
    print("=== STARTING PHASE 9E: EXECUTION RECONCILIATION TESTS ===")
    reconciler = ExecutionReconciler()
    pos_engine = PositionStateEngine(initial_capital=100000.0)

    # Test 1: Full Fill Order Reconciliation & Position Auto-Sync
    order1 = ExecutionOrder(order_id="REC_001", ticker="TATAMOTORS", side="BUY", qty=50, limit_price=980.0)
    order1.pass_precheck()
    order1.submit_to_broker("BROKER_1")
    order1.execute_fill(execution_price=981.0, qty=50) # 0.102% slippage

    audit1 = reconciler.reconcile(order1, pos_engine)
    assert audit1["status"] == "RECONCILED_MATCH"
    assert audit1["slippage_pct"] == 0.102
    assert "TATAMOTORS" in pos_engine.positions
    print("[PASS] Test 1 | Full Fill Order Reconciliation & Position Sync Verified")

    # Test 2: Terminated Order No-Op Verification (No Ghost Position)
    order2 = ExecutionOrder(order_id="REC_002", ticker="INFY", side="BUY", qty=30, limit_price=1500.0)
    order2.pass_precheck()
    order2.reject("Slippage limit violated")

    audit2 = reconciler.reconcile(order2, pos_engine)
    assert audit2["status"] == "TERMINATED_WITHOUT_FILL"
    assert "INFY" not in pos_engine.positions
    print("[PASS] Test 2 | Terminated Order Handled Without Portfolio Contamination")

    # Test 3: Partial Fill Reconciliation Tracking (Initial capital set to 200k to cover 40 * 2900 = 116k)
    pos_engine_2 = PositionStateEngine(initial_capital=200000.0)
    order3 = ExecutionOrder(order_id="REC_003", ticker="RELIANCE", side="BUY", qty=100, limit_price=2900.0)
    order3.pass_precheck()
    order3.submit_to_broker("BROKER_3")
    order3.execute_fill(execution_price=2900.0, qty=40) # Partial fill 40/100

    audit3 = reconciler.reconcile(order3, pos_engine_2)
    assert audit3["status"] == "RECONCILED_PARTIAL"
    assert audit3["filled_qty"] == 40
    assert pos_engine_2.positions["RELIANCE"].qty == 40
    print("[PASS] Test 3 | Partial Fill Position Reconciliation Verified")

    # Test 4: Position Liquidation Reconciliation
    pos_engine_2.update_market_price("RELIANCE", 2950.0)
    sell_order = ExecutionOrder(order_id="REC_004", ticker="RELIANCE", side="SELL", qty=40, limit_price=2940.0)
    sell_order.pass_precheck()
    sell_order.submit_to_broker("BROKER_4")
    sell_order.execute_fill(execution_price=2950.0, qty=40)

    audit4 = reconciler.reconcile(sell_order, pos_engine_2)
    assert audit4["status"] == "RECONCILED_MATCH"
    assert audit4["realized_pnl"] == 2000.0 # 40 * (2950 - 2900)
    assert "RELIANCE" not in pos_engine_2.positions
    print("[PASS] Test 4 | Position Exit Reconciliation & Realized PnL Accounting Verified")

    print("\nPhase 9E Execution Reconciliation Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase9e_tests()
