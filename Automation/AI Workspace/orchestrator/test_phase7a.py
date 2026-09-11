import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(Path(__file__).parent),
    str(runtime_path),
    str(runtime_path / "skills")
])

from rule_verification_suite import RuleVerificationSuite

def run_phase7a_tests():
    print("=== STARTING PHASE 7A: RULE VERIFICATION SKILL SUITE TESTS ===")
    suite = RuleVerificationSuite()

    # Test 1: Fully Compliant Proposal
    p1 = {"ticker": "TATAMOTORS", "proposed_risk_pct": 0.8, "positions_today": 0, "is_cash_trade": True, "is_shariah_compliant": True, "position_size_pct": 15.0}
    res1 = suite.execute(p1)
    assert res1["compliant"] is True
    assert res1["summary_status"] == "APPROVED"
    assert len(res1["passed_rules"]) == 5
    print("[PASS] Test 1 | Fully Compliant Trade Proposal Approved")

    # Test 2: Risk Limit Violation (> 1.0%)
    p2 = {"ticker": "INFY", "proposed_risk_pct": 1.5, "positions_today": 0, "is_cash_trade": True, "is_shariah_compliant": True, "position_size_pct": 10.0}
    res2 = suite.execute(p2)
    assert res2["compliant"] is False
    assert any("Risk Violation" in v for v in res2["violations"])
    print("[PASS] Test 2 | Excessive Risk Violation Caught")

    # Test 3: Daily Position Cap Exceeded
    p3 = {"ticker": "RELIANCE", "proposed_risk_pct": 0.5, "positions_today": 2, "is_cash_trade": True, "is_shariah_compliant": True, "position_size_pct": 10.0}
    res3 = suite.execute(p3)
    assert res3["compliant"] is False
    assert any("Frequency Violation" in v for v in res3["violations"])
    print("[PASS] Test 3 | Daily Frequency Limit Violation Caught")

    # Test 4: Non-Cash / Margin Violation
    p4 = {"ticker": "TCS", "proposed_risk_pct": 0.5, "positions_today": 0, "is_cash_trade": False, "is_shariah_compliant": True, "position_size_pct": 10.0}
    res4 = suite.execute(p4)
    assert res4["compliant"] is False
    assert any("Structure Violation" in v for v in res4["violations"])
    print("[PASS] Test 4 | Non-Cash / Leverage Violation Caught")

    # Test 5: Shariah Screening Violation
    p5 = {"ticker": "BANKBARODA", "proposed_risk_pct": 0.5, "positions_today": 0, "is_cash_trade": True, "is_shariah_compliant": False, "position_size_pct": 10.0}
    res5 = suite.execute(p5)
    assert res5["compliant"] is False
    assert any("Compliance Violation" in v for v in res5["violations"])
    print("[PASS] Test 5 | Non-Shariah Asset Violation Caught")

    # Test 6: Excess Position Allocation (> 20%)
    p6 = {"ticker": "HDFCBANK", "proposed_risk_pct": 0.8, "positions_today": 1, "is_cash_trade": True, "is_shariah_compliant": True, "position_size_pct": 25.0}
    res6 = suite.execute(p6)
    assert res6["compliant"] is False
    assert any("Allocation Violation" in v for v in res6["violations"])
    print("[PASS] Test 6 | Excess Position Size Allocation Caught")

    print("\nPhase 7A Rule Verification Suite Benchmark: 6/6 Passed")

if __name__ == "__main__":
    run_phase7a_tests()
