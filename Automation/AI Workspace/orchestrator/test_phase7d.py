import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(Path(__file__).parent),
    str(runtime_path),
    str(runtime_path / "skills")
])

from governance_check_suite import GovernanceCheckSuite

def run_phase7d_tests():
    print("=== STARTING PHASE 7D: GOVERNANCE & CONFLICT CHECK SKILL SUITE TESTS ===")
    gov = GovernanceCheckSuite()

    # Test 1: Governance Cleared
    t1 = {
        "ticker": "TATAMOTORS",
        "is_blacklisted": False,
        "earnings_within_48h": False,
        "portfolio_drawdown_pct": 1.2,
        "consecutive_losses": 1,
        "has_conflicting_order": False
    }
    res1 = gov.execute(t1)
    assert res1["governance_cleared"] is True
    assert res1["summary_status"] == "CLEARED"
    assert len(res1["passed_checks"]) == 5
    print("[PASS] Test 1 | Clean Governance Audit Cleared")

    # Test 2: Blacklisted Asset Intercept
    t2 = {
        "ticker": "BLACKLST_INC",
        "is_blacklisted": True,
        "earnings_within_48h": False,
        "portfolio_drawdown_pct": 1.0,
        "consecutive_losses": 0,
        "has_conflicting_order": False
    }
    res2 = gov.execute(t2)
    assert res2["governance_cleared"] is False
    assert any("Blacklist Intercept" in v for v in res2["violations"])
    print("[PASS] Test 2 | Blacklisted Asset Interception Verified")

    # Test 3: Earnings Event Lock Intercept
    t3 = {
        "ticker": "INFY",
        "is_blacklisted": False,
        "earnings_within_48h": True,
        "portfolio_drawdown_pct": 0.5,
        "consecutive_losses": 0,
        "has_conflicting_order": False
    }
    res3 = gov.execute(t3)
    assert res3["governance_cleared"] is False
    assert any("Event Lock" in v for v in res3["violations"])
    print("[PASS] Test 3 | Earnings Lock Period Interception Verified")

    # Test 4: System Circuit Breaker (Max Portfolio Drawdown Triggered)
    t4 = {
        "ticker": "RELIANCE",
        "is_blacklisted": False,
        "earnings_within_48h": False,
        "portfolio_drawdown_pct": 5.5, # Exceeds 5.0% cap
        "consecutive_losses": 0,
        "has_conflicting_order": False
    }
    res4 = gov.execute(t4)
    assert res4["governance_cleared"] is False
    assert any("Circuit Breaker" in v for v in res4["violations"])
    print("[PASS] Test 4 | Portfolio Drawdown Circuit Breaker Triggered")

    # Test 5: Order Conflict Intercept
    t5 = {
        "ticker": "TCS",
        "is_blacklisted": False,
        "earnings_within_48h": False,
        "portfolio_drawdown_pct": 1.0,
        "consecutive_losses": 0,
        "has_conflicting_order": True
    }
    res5 = gov.execute(t5)
    assert res5["governance_cleared"] is False
    assert any("Conflict Intercept" in v for v in res5["violations"])
    print("[PASS] Test 5 | Active Order Conflict Interception Verified")

    print("\nPhase 7D Governance & Conflict Check Suite Benchmark: 5/5 Passed")

if __name__ == "__main__":
    run_phase7d_tests()
