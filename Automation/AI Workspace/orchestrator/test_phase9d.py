import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from execution_state_machine import ExecutionOrder, OrderState
from order_simulation_engine import OrderSimulationEngine

def run_phase9d_tests():
    print("=== STARTING PHASE 9D: ORDER SIMULATION ENGINE TESTS ===")
    sim_engine = OrderSimulationEngine(default_slippage_pct=0.1)

    # Test 1: Full Fill Match
    order1 = ExecutionOrder(order_id="SIM_001", ticker="TATAMOTORS", side="BUY", qty=100, limit_price=980.0)
    order1.pass_precheck()
    order1.submit_to_broker("SIM_BROKER_1")

    market1 = {"ask": 979.0, "bid": 978.5, "volume": 500}
    res1 = sim_engine.simulate_fill(order1, market1)
    assert res1["status"] == "FILLED"
    assert order1.state == OrderState.FILLED
    print("[PASS] Test 1 | Complete Simulated Order Fill Executed")

    # Test 2: Unfilled Due to Limit Boundary Exceeded
    order2 = ExecutionOrder(order_id="SIM_002", ticker="INFY", side="BUY", qty=50, limit_price=1500.0)
    order2.pass_precheck()
    order2.submit_to_broker("SIM_BROKER_2")

    market2 = {"ask": 1520.0, "bid": 1518.0, "volume": 1000}
    res2 = sim_engine.simulate_fill(order2, market2)
    assert res2["status"] == "UNFILLED"
    assert order2.state == OrderState.SUBMITTED
    print("[PASS] Test 2 | Out-of-Bounds Market Price Prevented Fill")

    # Test 3: Partial Fill Simulation
    order3 = ExecutionOrder(order_id="SIM_003", ticker="RELIANCE", side="BUY", qty=100, limit_price=2900.0)
    order3.pass_precheck()
    order3.submit_to_broker("SIM_BROKER_3")

    market3 = {"ask": 2895.0, "bid": 2890.0, "volume": 40} # Only 40 shares available
    res3 = sim_engine.simulate_fill(order3, market3)
    assert res3["status"] == "PARTIALLY_FILLED"
    assert order3.state == OrderState.PARTIALLY_FILLED
    assert order3.filled_qty == 40
    print("[PASS] Test 3 | Liquidity-Constrained Partial Fill Handled")

    # Test 4: Simulated Excessive Slippage Rejection
    sim_high_slip = OrderSimulationEngine(default_slippage_pct=1.0) # 1.0% > 0.5% max allowed
    order4 = ExecutionOrder(order_id="SIM_004", ticker="TCS", side="BUY", qty=10, limit_price=4000.0, max_slippage_pct=0.5)
    order4.pass_precheck()
    order4.submit_to_broker("SIM_BROKER_4")

    market4 = {"ask": 4000.0, "bid": 3995.0, "volume": 100}
    res4 = sim_high_slip.simulate_fill(order4, market4)
    assert res4["status"] == "REJECTED"
    assert order4.state == OrderState.REJECTED
    print("[PASS] Test 4 | Simulated Slippage Violation Resulted in Order Rejection")

    print("\nPhase 9D Order Simulation Engine Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase9d_tests()
