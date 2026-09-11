import sys
import json
from pathlib import Path

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(Path(__file__).parent),
    str(runtime_path),
    str(runtime_path / "router"),
    str(runtime_path / "permissions"),
    str(runtime_path / "skills"),
    str(runtime_path / "memory")
])

from orchestrator import AgentOrchestrator

def run_phase6d_e2e_tests():
    print("=== STARTING PHASE 6D END-TO-END ORCHESTRATOR INTEGRATION TESTS ===")
    
    orchestrator = AgentOrchestrator()

    # Test E2E-01: Compliant Trade Precheck Query
    res_01 = orchestrator.execute_orchestration(
        "Can I open a trade on INFYS with 0.5% risk?",
        "e2e_sess_01",
        {"proposed_risk_pct": 0.5, "positions_today": 1, "is_cash_trade": True}
    )
    assert res_01["status"] == "SUCCESS"
    assert res_01["intent"] == "TRADE_PRECHECK"
    assert res_01["memory_logged"] is True
    assert "synthesis" in res_01
    print("[PASS] TC-E2E-01 | Compliant Trade Precheck E2E Flow")

    # Test E2E-02: Non-Compliant Trade Precheck Query (High Risk)
    res_02 = orchestrator.execute_orchestration(
        "Can I buy RELIANCE with 2.5% risk?",
        "e2e_sess_02",
        {"proposed_risk_pct": 2.5, "positions_today": 0, "is_cash_trade": True}
    )
    assert res_02["status"] == "SUCCESS"
    skill_out = next(r for r in res_02["step_results"] if r.get("component") == "SKILL")
    assert skill_out["compliant"] is False
    assert len(skill_out["violations"]) > 0
    print("[PASS] TC-E2E-02 | Non-Compliant Trade Precheck Skill Intercept")

    # Test E2E-03: Mutation Attempt Intercept (Firewall Block)
    res_03 = orchestrator.execute_orchestration(
        "delete rule 101 from vault",
        "e2e_sess_03"
    )
    assert res_03["status"] == "BLOCKED"
    assert res_03["orchestration_phase"] == "FIREWALL_INTERCEPT"
    print("[PASS] TC-E2E-03 | Mutation Query Firewall Intercept & Memory Logging")

    # Test E2E-04: Strategy Lookup Flow
    res_04 = orchestrator.execute_orchestration(
        "Explain the entry criteria for the EMA20-50 Pullback strategy.",
        "e2e_sess_04"
    )
    assert res_04["status"] == "SUCCESS"
    assert res_04["intent"] == "STRATEGY_LOOKUP"
    assert res_04["authority_rank"] == 2
    print("[PASS] TC-E2E-04 | Strategy Lookup E2E Execution & Rank 2 Routing")

    print("\nPhase 6D E2E Integration Benchmark Result: 4/4 Passed")

if __name__ == "__main__":
    run_phase6d_e2e_tests()
