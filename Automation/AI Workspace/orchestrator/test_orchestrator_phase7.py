import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from router import OrchestratorRouter

def run_orchestrator_integration_tests():
    print("=== STARTING INTEGRATED ORCHESTRATOR ROUTER TESTS (PHASE 7) ===")
    router = OrchestratorRouter()

    trade_payload = {
        "ticker": "TATAMOTORS",
        "is_blacklisted": False,
        "earnings_within_48h": False,
        "portfolio_drawdown_pct": 1.2,
        "consecutive_losses": 0,
        "has_conflicting_order": False,
        "proposed_risk_pct": 0.8,
        "positions_today": 0,
        "is_cash_trade": True,
        "is_shariah_compliant": True,
        "position_size_pct": 10.0,
        "close_price": 980.0,
        "ema20": 978.0,
        "ema50": 950.0,
        "vwap": 975.0,
        "rsi": 52.0,
        "risk_reward_ratio": 1.8
    }

    # Test 1: Route to SOP Execution Assistant
    res1 = router.route_and_execute("SOP_EXECUTION", trade_payload)
    assert res1["status"] == "SUCCESS"
    assert res1["result"]["execution_decision"] == "EXECUTE"
    print("[PASS] Test 1 | Intent 'SOP_EXECUTION' routed and executed successfully")

    # Test 2: Direct Route to Governance Check
    res2 = router.route_and_execute("GOVERNANCE_CHECK", trade_payload)
    assert res2["status"] == "SUCCESS"
    assert res2["result"]["governance_cleared"] is True
    print("[PASS] Test 2 | Intent 'GOVERNANCE_CHECK' routed successfully")

    # Test 3: Unregistered Intent Handling
    res3 = router.route_and_execute("INVALID_INTENT", trade_payload)
    assert res3["status"] == "ERROR"
    print("[PASS] Test 3 | Fallback error correctly returned for unregistered intent")

    print("\nPhase 7 Integrated Orchestrator Router Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_orchestrator_integration_tests()
