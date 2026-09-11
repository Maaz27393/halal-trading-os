import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from broker_session_manager import BrokerSessionManager
from live_readiness_auditor import LiveReadinessAuditor

def run_phase12a_tests():
    print("=== STARTING PHASE 12A: LIVE READINESS GATE & STATE RECONCILER TESTS ===")
    
    broker = BrokerSessionManager(broker_name="Shoonya")
    broker.authenticate("MOCK_KEY", "USER123", "123456")
    auditor = LiveReadinessAuditor(broker_session=broker, max_risk_per_trade_pct=1.0, max_trades_per_day=2)

    # Test 1: Broker Session & Connectivity Audit
    conn_audit = auditor.audit_broker_connectivity()
    assert conn_audit["ready"] is True
    print("[PASS] Test 1 | Live Broker Connectivity & Session Audit Verified")

    # Test 2: Local vs Broker Account State Reconciliation
    local_state = {"available_cash": 100000.0, "open_positions": [], "open_orders": []}
    broker_state = {"available_cash": 100000.0, "open_positions": [], "open_orders": []}

    rec1 = auditor.reconcile_account_state(local_state, broker_state)
    assert rec1["reconciled"] is True
    assert rec1["status"] == "STATE_RECONCILED"

    drifted_broker_state = {"available_cash": 95000.0, "open_positions": [1], "open_orders": []}
    rec2 = auditor.reconcile_account_state(local_state, drifted_broker_state)
    assert rec2["reconciled"] is False
    assert rec2["drift_count"] == 2
    assert rec2["status"] == "DESYNCHRONIZATION_DETECTED"
    print("[PASS] Test 2 | Account State Reconciliation & Drift Detection Verified")

    # Test 3: Hard Risk Invariant Enforcements
    valid_trade = {
        "product_type": "CNC", # Cash & Carry Delivery
        "risk_amount": 800.0,  # 0.8% of 100,000 equity
        "risk_reward_ratio": 1.8
    }
    res_valid = auditor.verify_risk_invariants(valid_trade, total_equity=100000.0, trades_today_count=0)
    assert res_valid["passed"] is True

    # Violation: High Risk (> 1%)
    high_risk_trade = {"product_type": "CNC", "risk_amount": 1500.0, "risk_reward_ratio": 2.0}
    res_risk = auditor.verify_risk_invariants(high_risk_trade, total_equity=100000.0, trades_today_count=0)
    assert res_risk["passed"] is False
    assert "EXCEEDS_MAX_RISK_PER_TRADE" in res_risk["reason"]

    # Violation: Restricted Product Type (Derivatives/F&O)
    fo_trade = {"product_type": "FUTURES", "risk_amount": 500.0, "risk_reward_ratio": 2.0}
    res_fo = auditor.verify_risk_invariants(fo_trade, total_equity=100000.0, trades_today_count=0)
    assert res_fo["passed"] is False
    assert "UNAUTHORIZED_PRODUCT_TYPE" in res_fo["reason"]
    print("[PASS] Test 3 | Immutable Risk Invariants & Product Restrictions Verified")

    print("\nPhase 12A Live Readiness Gate Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase12a_tests()
