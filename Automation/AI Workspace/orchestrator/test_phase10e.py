import sys
import time
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from walk_forward_validator import WalkForwardValidator

def run_phase10e_tests():
    print("=== STARTING PHASE 10E: WALK-FORWARD VALIDATION TESTS ===")
    wf = WalkForwardValidator(is_ratio=0.70)

    now = int(time.time())
    mock_candles = [{"timestamp_epoch": now + (i * 60), "close": 100 + i} for i in range(100)]

    # Test 1: Chronological Dataset Splitting
    is_feed, oos_feed = wf.split_chronological_feed(mock_candles)
    assert len(is_feed) == 70
    assert len(oos_feed) == 30
    assert is_feed[-1]["timestamp_epoch"] < oos_feed[0]["timestamp_epoch"]
    print("[PASS] Test 1 | Chronological IS/OOS Data Splitting Verified")

    # Test 2: High Efficiency Robust Strategy Evaluation
    is_metrics_good = {"net_profit": 14000.0, "expectancy_per_trade": 200.0}
    oos_metrics_good = {"net_profit": 5000.0, "expectancy_per_trade": 150.0} # 150/200 = 75% WFE
    
    wfe_res_good = wf.calculate_wfe(is_metrics_good, oos_metrics_good)
    assert wfe_res_good["wfe_ratio_pct"] == 75.0
    assert wfe_res_good["is_robust"] is True
    assert wfe_res_good["overfit_warning"] is False
    print("[PASS] Test 2 | Robust Non-Overfitted WFE Metric Calculation Verified")

    # Test 3: Overfitted Strategy Failure Interception
    is_metrics_overfit = {"net_profit": 20000.0, "expectancy_per_trade": 500.0}
    oos_metrics_overfit = {"net_profit": -2000.0, "expectancy_per_trade": -50.0} # Collapse in OOS
    
    wfe_res_overfit = wf.calculate_wfe(is_metrics_overfit, oos_metrics_overfit)
    assert wfe_res_overfit["is_robust"] is False
    assert wfe_res_overfit["overfit_warning"] is True
    print("[PASS] Test 3 | Overfitted Strategy Degradation Detection Verified")

    print("\nPhase 10E Walk-Forward Validation Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase10e_tests()
