import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from pre_execution_revalidation import PreExecutionRevalidator

def run_phase9c_tests():
    print("=== STARTING PHASE 9C: PRE-EXECUTION REVALIDATION TESTS ===")
    revalidator = PreExecutionRevalidator(max_stale_seconds=5.0, max_price_drift_pct=0.8)

    order = {
        "ticker": "TATAMOTORS",
        "limit_price": 980.0,
        "qty": 50
    }

    # Test 1: Clean Last-Second Pass
    now = time.time()
    candle_clean = {"close": 982.0, "timestamp_epoch": now} # 0.20% drift
    res1 = revalidator.revalidate(order, candle_clean, available_capital=100000.0)
    assert res1["revalidated"] is True
    print("[PASS] Test 1 | Clean Pre-Execution Revalidation Passed")

    # Test 2: Price Drift Boundary Violation
    candle_drifted = {"close": 995.0, "timestamp_epoch": now} # 1.53% drift > 0.8%
    res2 = revalidator.revalidate(order, candle_drifted, available_capital=100000.0)
    assert res2["revalidated"] is False
    assert "Price drift limit exceeded" in res2["reason"]
    print("[PASS] Test 2 | Excessive Price Drift Intercepted")

    # Test 3: Stale Data Interception
    candle_stale = {"close": 981.0, "timestamp_epoch": now - 10.0} # 10s old > 5s limit
    res3 = revalidator.revalidate(order, candle_stale, available_capital=100000.0)
    assert res3["revalidated"] is False
    assert "Stale market data" in res3["reason"]
    print("[PASS] Test 3 | Stale Market Feed Rejection Verified")

    # Test 4: Last-Second Capital Depletion
    res4 = revalidator.revalidate(order, candle_clean, available_capital=20000.0) # Requires 49,000
    assert res4["revalidated"] is False
    assert "Capital insufficient" in res4["reason"]
    print("[PASS] Test 4 | Last-Second Capital Depletion Protection Verified")

    print("\nPhase 9C Pre-Execution Revalidation Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase9c_tests()
