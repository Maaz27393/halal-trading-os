import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(Path(__file__).parent),
    str(runtime_path),
    str(runtime_path / "skills")
])

from trade_precheck_suite import TradePrecheckSuite

def run_phase7c_tests():
    print("=== STARTING PHASE 7C: TRADE PRE-CHECK SKILL SUITE TESTS ===")
    precheck = TradePrecheckSuite()

    # Test 1: Fully Approved Trade Proposal
    t1 = {
        "ticker": "TATAMOTORS",
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
    res1 = precheck.execute(t1)
    assert res1["overall_approved"] is True
    assert res1["precheck_status"] == "APPROVED"
    print("[PASS] Test 1 | Fully Compliant & Technically Valid Trade Approved")

    # Test 2: Rule Failure + Strategy Pass
    t2 = {
        "ticker": "INFY",
        "proposed_risk_pct": 1.8, # Excessive Risk
        "positions_today": 0,
        "is_cash_trade": True,
        "is_shariah_compliant": True,
        "position_size_pct": 10.0,
        "close_price": 1500.0,
        "ema20": 1498.0,
        "ema50": 1450.0,
        "vwap": 1495.0,
        "rsi": 50.0,
        "risk_reward_ratio": 2.0
    }
    res2 = precheck.execute(t2)
    assert res2["overall_approved"] is False
    assert res2["precheck_status"] == "REJECTED_RULES"
    print("[PASS] Test 2 | Rule Failure Correctly Triggers REJECTED_RULES")

    # Test 3: Rule Pass + Strategy Failure
    t3 = {
        "ticker": "RELIANCE",
        "proposed_risk_pct": 0.5,
        "positions_today": 0,
        "is_cash_trade": True,
        "is_shariah_compliant": True,
        "position_size_pct": 10.0,
        "close_price": 2900.0,
        "ema20": 2800.0, # Overextended
        "ema50": 2700.0,
        "vwap": 2850.0,
        "rsi": 75.0,
        "risk_reward_ratio": 1.6
    }
    res3 = precheck.execute(t3)
    assert res3["overall_approved"] is False
    assert res3["precheck_status"] == "REJECTED_STRATEGY"
    print("[PASS] Test 3 | Technical Setup Failure Triggers REJECTED_STRATEGY")

    # Test 4: Combined Failure (Both Rules and Strategy Fail)
    t4 = {
        "ticker": "BANKBARODA",
        "proposed_risk_pct": 2.0, # Excessive risk
        "positions_today": 0,
        "is_cash_trade": True,
        "is_shariah_compliant": False, # Non-compliant
        "position_size_pct": 10.0,
        "close_price": 200.0,
        "ema20": 210.0, # Bearish EMA alignment
        "ema50": 220.0,
        "vwap": 215.0,
        "rsi": 30.0,
        "risk_reward_ratio": 1.1
    }
    res4 = precheck.execute(t4)
    assert res4["overall_approved"] is False
    assert res4["precheck_status"] == "REJECTED_MULTIPLE"
    print("[PASS] Test 4 | Dual Failures Trigger REJECTED_MULTIPLE")

    print("\nPhase 7C Integrated Trade Pre-Check Suite Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase7c_tests()
