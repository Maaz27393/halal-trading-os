import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from market_data_adapter import MarketDataAdapter

def run_phase9a_tests():
    print("=== STARTING PHASE 9A: MARKET DATA ADAPTER TESTS ===")
    adapter = MarketDataAdapter()

    # Test 1: Valid Tick Normalization
    raw1 = {
        "ticker": "tatamotors",
        "open": 975.0,
        "high": 985.0,
        "low": 970.0,
        "close": 980.0,
        "volume": 150000,
        "vwap": 978.5
    }
    res1 = adapter.normalize_candle(raw1)
    assert res1["is_valid"] is True
    assert res1["normalized_data"]["ticker"] == "TATAMOTORS"
    assert res1["normalized_data"]["close"] == 980.0
    print("[PASS] Test 1 | Standard NSE Candle Data Successfully Normalized")

    # Test 2: Invalid Pricing (High < Low Boundary Breach)
    raw2 = {
        "ticker": "INFY",
        "open": 1500.0,
        "high": 1480.0,
        "low": 1510.0,
        "close": 1500.0,
        "volume": 50000
    }
    res2 = adapter.normalize_candle(raw2)
    assert res2["is_valid"] is False
    assert res2["error"] == "HIGH_LOW_OUT_OF_BOUNDS"
    print("[PASS] Test 2 | High/Low Bound Breach Correctly Intercepted")

    # Test 3: Zero or Negative Price Protection
    raw3 = {
        "ticker": "RELIANCE",
        "close": -10.0,
        "volume": 1000
    }
    res3 = adapter.normalize_candle(raw3)
    assert res3["is_valid"] is False
    assert res3["error"] == "NON_POSITIVE_PRICE"
    print("[PASS] Test 3 | Non-Positive Pricing Correctly Rejected")

    print("\nPhase 9A Market Data Adapter Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase9a_tests()
