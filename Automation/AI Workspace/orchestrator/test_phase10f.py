import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from paper_vs_backtest_auditor import PaperVsBacktestAuditor

def run_phase10f_tests():
    print("=== STARTING PHASE 10F: PAPER-VS-BACKTEST CONSISTENCY AUDITOR TESTS ===")
    auditor = PaperVsBacktestAuditor(tolerance_pct=0.01)

    # Identical Mock Run Data
    paper_res = {
        "executed_trades": 5,
        "final_portfolio": {
            "total_equity": 210500.0,
            "open_positions_count": 0,
            "total_realized_pnl": 10500.0
        }
    }

    backtest_res = {
        "executed_trades": 5,
        "final_portfolio": {
            "total_equity": 210500.0,
            "open_positions_count": 0,
            "total_realized_pnl": 10500.0
        }
    }

    # Test 1: Zero-Drift Parity Verification
    audit1 = auditor.audit_runs(paper_res, backtest_res)
    assert audit1["parity_passed"] is True
    assert audit1["drift_count"] == 0
    assert audit1["audit_summary"] == "ZERO_DRIFT_VERIFIED"
    print("[PASS] Test 1 | Zero-Drift Engine Parity Audit Verified")

    # Divergent Run Data (Simulated Drift)
    drifted_backtest_res = {
        "executed_trades": 4, # Mismatch
        "final_portfolio": {
            "total_equity": 208000.0, # Mismatch
            "open_positions_count": 1, # Mismatch
            "total_realized_pnl": 8000.0
        }
    }

    # Test 2: Execution Drift Detection & Interception
    audit2 = auditor.audit_runs(paper_res, drifted_backtest_res)
    assert audit2["parity_passed"] is False
    assert audit2["drift_count"] >= 3
    assert audit2["audit_summary"] == "DRIFT_DETECTED"
    print("[PASS] Test 2 | Logic & State Divergence Detection Verified")

    print("\nPhase 10F Paper-vs-Backtest Auditor Benchmark: 2/2 Passed")

if __name__ == "__main__":
    run_phase10f_tests()
