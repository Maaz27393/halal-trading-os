import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(Path(__file__).parent),
    str(runtime_path),
    str(runtime_path / "skills")
])

from sop_execution_assistant import SOPExecutionAssistant

def run_phase7e_tests():
    print("=== STARTING PHASE 7E: SOP EXECUTION ASSISTANT SKILL SUITE TESTS ===")
    assistant = SOPExecutionAssistant()

    # Test 1: Full E2E Execution Approval
    t1 = {
        "ticker": "TATAMOTORS",
        "is_blacklisted": False,
        "earnings_within_48h": False,
        "portfolio_drawdown_pct": 1.0,
        "consecutive_losses": 0,
        "has_conflicting_order": False,
        "proposed_risk_pct": 0.8,
        "positions_today": 0,
        "is_cash_trade": True,
        "is_shariah_compliant": True,
        "position_size_pct": 12.0,
        "close_price": 980.0,
        "ema20": 978.0,
        "ema50": 950.0,
        "vwap": 975.0,
        "rsi": 52.0,
        "risk_reward_ratio": 1.8
    }
    res1 = assistant.execute(t1)
    assert res1["is_approved"] is True
    assert res1["execution_decision"] == "EXECUTE"
    print("[PASS] Test 1 | Full E2E Pre-Flight Audit Approved")

    # Test 2: Intercepted at Governance Layer (Max Drawdown Trigger)
    t2 = {
        "ticker": "TATAMOTORS",
        "is_blacklisted": False,
        "earnings_within_48h": False,
        "portfolio_drawdown_pct": 6.0, # Excessive Drawdown
        "consecutive_losses": 0,
        "has_conflicting_order": False,
        "proposed_risk_pct": 0.8,
        "positions_today": 0,
        "is_cash_trade": True,
        "is_shariah_compliant": True,
        "position_size_pct": 12.0,
        "close_price": 980.0,
        "ema20": 978.0,
        "ema50": 950.0,
        "vwap": 975.0,
        "rsi": 52.0,
        "risk_reward_ratio": 1.8
    }
    res2 = assistant.execute(t2)
    assert res2["is_approved"] is False
    assert res2["execution_decision"] == "REJECTED_GOVERNANCE"
    print("[PASS] Test 2 | Governance Circuit Breaker Overrides Valid Technical Setup")

    # Test 3: Governance Pass, Intercepted at Trade Precheck Layer (Non-Shariah)
    t3 = {
        "ticker": "NON_SHARIAH_CO",
        "is_blacklisted": False,
        "earnings_within_48h": False,
        "portfolio_drawdown_pct": 0.5,
        "consecutive_losses": 0,
        "has_conflicting_order": False,
        "proposed_risk_pct": 0.8,
        "positions_today": 0,
        "is_cash_trade": True,
        "is_shariah_compliant": False, # Shariah Violation
        "position_size_pct": 10.0,
        "close_price": 500.0,
        "ema20": 498.0,
        "ema50": 480.0,
        "vwap": 495.0,
        "rsi": 50.0,
        "risk_reward_ratio": 2.0
    }
    res3 = assistant.execute(t3)
    assert res3["is_approved"] is False
    assert "REJECTED_PRECHECK" in res3["execution_decision"]
    print("[PASS] Test 3 | Compliance Rule Interception Correctly Propagated")

    print("\nPhase 7E SOP Execution Assistant Skill Suite Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase7e_tests()
