import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from event_simulation_engine import EventSimulationEngine

def run_phase10c_tests():
    print("=== STARTING PHASE 10C: EVENT SIMULATION ENGINE TESTS ===")
    sim = EventSimulationEngine(circuit_limit_pct=10.0, max_volume_participation_pct=0.10)

    now = int(time.time())
    base_candle = {
        "ticker": "TATAMOTORS",
        "open": 1000.0,
        "high": 1020.0,
        "low": 990.0,
        "close": 1010.0,
        "volume": 5000,
        "bid": 1009.5,
        "ask": 1010.5,
        "timestamp_epoch": now
    }

    # Test 1: Overnight Price Gap Injection
    gapped_candle = sim.apply_price_gap(base_candle, gap_pct=5.0) # +5% gap
    assert gapped_candle["open"] == 1050.0
    assert gapped_candle["close"] == 1060.5
    assert gapped_candle["high"] >= 1050.0
    print("[PASS] Test 1 | Price Gap Injection Mechanics Verified")

    # Test 2: Circuit Breaker Halt Detection
    halt_candle = {"close": 1120.0} # 12% jump from 1000.0 reference (> 10% limit)
    is_halted = sim.check_circuit_breaker(halt_candle, reference_close=1000.0)
    assert is_halted is True
    
    normal_candle = {"close": 1040.0} # 4% change
    is_halted_normal = sim.check_circuit_breaker(normal_candle, reference_close=1000.0)
    assert is_halted_normal is False
    print("[PASS] Test 2 | Circuit Breaker Trading Halt Interception Verified")

    # Test 3: Volume-Cap Partial Fill Calculation
    # Requested 1000 shares against 5000 bar volume (10% cap = max 500 shares)
    fill_qty, is_partial = sim.calculate_volume_fill(requested_qty=1000, candle_volume=5000)
    assert fill_qty == 500
    assert is_partial is True

    # Requested 300 shares against 5000 bar volume (under 500 cap)
    fill_qty2, is_partial2 = sim.calculate_volume_fill(requested_qty=300, candle_volume=5000)
    assert fill_qty2 == 300
    assert is_partial2 is False
    print("[PASS] Test 3 | Volume-Participation Partial Fill Cap Verified")

    # Test 4: Volatility Slippage Expansion
    buy_price = sim.calculate_stress_slippage(base_price=1000.0, side="BUY", volatility_multiplier=4.0, base_slippage_pct=0.05)
    # 0.05% * 4 = 0.20% slippage -> 1000 * 1.002 = 1002.0
    assert buy_price == 1002.0

    sell_price = sim.calculate_stress_slippage(base_price=1000.0, side="SELL", volatility_multiplier=4.0, base_slippage_pct=0.05)
    assert sell_price == 998.0
    print("[PASS] Test 4 | Stress Volatility Slippage Calculation Verified")

    print("\nPhase 10C Event Simulation Engine Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase10c_tests()
