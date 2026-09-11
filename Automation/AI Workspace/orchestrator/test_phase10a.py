import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from historical_data_adapter import HistoricalDataAdapter

def run_phase10a_tests():
    print("=== STARTING PHASE 10A: HISTORICAL DATA ADAPTER TESTS ===")
    adapter = HistoricalDataAdapter(default_spread_pct=0.1)

    now = int(time.time())

    raw_tata = [
        {"timestamp_epoch": now, "open": 980.0, "high": 985.0, "low": 978.0, "close": 982.0, "volume": 15000},
        {"timestamp_epoch": now + 60, "open": 982.0, "high": 990.0, "low": 981.0, "close": 988.0, "volume": 22000},
        {"timestamp_epoch": now + 120, "open": 988.0, "high": 995.0, "low": 985.0, "close": 991.0, "volume": 18000}
    ]

    raw_infy = [
        {"timestamp_epoch": now + 30, "open": 1500.0, "high": 1505.0, "low": 1495.0, "close": 1502.0, "volume": 10000},
        {"timestamp_epoch": now + 90, "open": 1502.0, "high": 1512.0, "low": 1500.0, "close": 1510.0, "volume": 14000}
    ]

    # Test 1: Single Ticker Record Normalization
    candles_tata = adapter.normalize_candles(raw_tata, "TATAMOTORS")
    assert len(candles_tata) == 3
    assert candles_tata[0]["ticker"] == "TATAMOTORS"
    assert candles_tata[0]["ask"] > candles_tata[0]["close"]
    assert candles_tata[0]["bid"] < candles_tata[0]["close"]
    print("[PASS] Test 1 | Single Ticker OHLCV Normalization & Bid/Ask Generation Verified")

    # Test 2: Multi-Symbol Interleaved Chronological Feed Creation
    multi_feed = adapter.create_multi_symbol_feed({"TATAMOTORS": raw_tata, "INFY": raw_infy})
    assert len(multi_feed) == 5
    timestamps = [c["timestamp_epoch"] for c in multi_feed]
    assert timestamps == sorted(timestamps)
    assert multi_feed[1]["ticker"] == "INFY"
    print("[PASS] Test 2 | Multi-Symbol Chronological Stream Interleaving Verified")

    # Test 3: Generator Tick Streaming
    stream = adapter.stream_ticks(multi_feed)
    first_tick = next(stream)
    assert first_tick["ticker"] == "TATAMOTORS"
    assert first_tick["close"] == 982.0
    print("[PASS] Test 3 | Sequential Generator Tick Streaming Verified")

    print("\nPhase 10A Historical Data Adapter Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase10a_tests()
