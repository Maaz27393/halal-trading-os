import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(Path(__file__).parent),
    str(runtime_path),
    str(runtime_path / "skills")
])

from strategy_analysis_suite import StrategyAnalysisSuite

def run_phase7b_tests():
    print("=== STARTING PHASE 7B: STRATEGY ANALYSIS SKILL SUITE TESTS ===")
    suite = StrategyAnalysisSuite()

    # Test 1: Valid EMA Pullback Setup
    setup1 = {
        "ticker": "TATAMOTORS",
        "strategy_name": "EMA_PULLBACK",
        "close_price": 980.0,
        "ema20": 978.0,
        "ema50": 950.0,
        "vwap": 975.0,
        "rsi": 52.0,
        "risk_reward_ratio": 1.8
    }
    res1 = suite.execute(setup1)
    assert res1["valid_setup"] is True
    assert res1["summary_status"] == "VALID_SETUP"
    assert len(res1["passed_checks"]) == 5
    print("[PASS] Test 1 | Valid EMA Pullback Setup Approved")

    # Test 2: Trend Alignment Failure (EMA20 < EMA50)
    setup2 = {
        "ticker": "INFY",
        "strategy_name": "EMA_PULLBACK",
        "close_price": 1400.0,
        "ema20": 1390.0,
        "ema50": 1420.0,
        "vwap": 1395.0,
        "rsi": 45.0,
        "risk_reward_ratio": 2.0
    }
    res2 = suite.execute(setup2)
    assert res2["valid_setup"] is False
    assert any("Trend Alignment Failure" in f for f in res2["failed_checks"])
    print("[PASS] Test 2 | Bearish EMA Alignment Correctly Rejected")

    # Test 3: Extended Price (Failed Pullback Proximity)
    setup3 = {
        "ticker": "RELIANCE",
        "strategy_name": "EMA_PULLBACK",
        "close_price": 2900.0,
        "ema20": 2800.0,
        "ema50": 2700.0,
        "vwap": 2850.0,
        "rsi": 72.0,
        "risk_reward_ratio": 1.6
    }
    res3 = suite.execute(setup3)
    assert res3["valid_setup"] is False
    assert any("Pullback Proximity Failure" in f for f in res3["failed_checks"])
    print("[PASS] Test 3 | Overextended Setup Correctly Rejected")

    # Test 4: Below VWAP Failure
    setup4 = {
        "ticker": "TCS",
        "strategy_name": "EMA_PULLBACK",
        "close_price": 3800.0,
        "ema20": 3795.0,
        "ema50": 3700.0,
        "vwap": 3820.0,
        "rsi": 48.0,
        "risk_reward_ratio": 1.7
    }
    res4 = suite.execute(setup4)
    assert res4["valid_setup"] is False
    assert any("VWAP Alignment Failure" in f for f in res4["failed_checks"])
    print("[PASS] Test 4 | Below VWAP Setup Correctly Rejected")

    # Test 5: Insufficient Risk-Reward Ratio (< 1.5)
    setup5 = {
        "ticker": "HDFCBANK",
        "strategy_name": "EMA_PULLBACK",
        "close_price": 1600.0,
        "ema20": 1598.0,
        "ema50": 1550.0,
        "vwap": 1595.0,
        "rsi": 55.0,
        "risk_reward_ratio": 1.2
    }
    res5 = suite.execute(setup5)
    assert res5["valid_setup"] is False
    assert any("Risk-Reward Failure" in f for f in res5["failed_checks"])
    print("[PASS] Test 5 | Low R:R Ratio Setup Correctly Rejected")

    print("\nPhase 7B Strategy Analysis Suite Benchmark: 5/5 Passed")

if __name__ == "__main__":
    run_phase7b_tests()
