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
from failure_stress_harness import FailureStressHarness
from shadow_execution_engine import ShadowExecutionEngine
from phase12_master_orchestrator import Phase12MasterOrchestrator

def run_phase12_master_tests():
    print("=== STARTING PHASE 12 MASTER INTEGRATION & GOVERNANCE TESTS ===")

    broker = BrokerSessionManager(broker_name="Shoonya")
    broker.authenticate("MOCK_KEY", "USER123", "123456")

    auditor = LiveReadinessAuditor(broker_session=broker, max_risk_per_trade_pct=1.0, max_trades_per_day=2)
    harness = FailureStressHarness(max_allowed_slippage_pct=0.5)
    shadow_engine = ShadowExecutionEngine(readiness_auditor=auditor, stress_harness=harness)

    orchestrator = Phase12MasterOrchestrator(
        broker_session=broker,
        auditor=auditor,
        stress_harness=harness,
        shadow_engine=shadow_engine
    )

    account_state = {"available_cash": 100000.0, "invested_value": 0.0, "trades_today_count": 0}

    # Test 1: Shadow Signal Execution via Master Pipeline
    sig1 = {
        "trading_symbol": "TCS-EQ",
        "action": "BUY",
        "quantity": 5,
        "trigger_price": 3800.0,
        "risk_amount": 500.0,
        "risk_reward_ratio": 2.0,
        "product_type": "DELIVERY"
    }
    res1 = orchestrator.process_incoming_signal(sig1, market_price=3802.0, account_state=account_state)
    assert res1["status"] == "FILLED_SHADOW"
    print("[PASS] Test 1 | Master Pipeline Shadow Dispatch & Verification")

    # Test 2: Emergency Kill Switch Triggering
    ks_res = orchestrator.trigger_kill_switch("MANUAL_PANIC_BUTTON_PRESSED")
    assert ks_res["kill_switch_active"] is True
    assert ks_res["status"] == "SYSTEM_HALTED"
    print("[PASS] Test 2 | Emergency Kill Switch Activation Verified")

    # Test 3: Interception of Signal Post-Kill Switch Activation
    res2 = orchestrator.process_incoming_signal(sig1, market_price=3802.0, account_state=account_state)
    assert res2["status"] == "REJECTED_KILL_SWITCH_ACTIVE"
    print("[PASS] Test 3 | Immediate Signal Rejection During Active Kill Switch Verified")

    # Test 4: Reset Kill Switch & Resume
    orchestrator.reset_kill_switch()
    res3 = orchestrator.process_incoming_signal(sig1, market_price=3802.0, account_state=account_state)
    assert res3["status"] == "FILLED_SHADOW"
    print("[PASS] Test 4 | Kill Switch Reset & Pipeline Recovery Verified")

    print("\nPhase 12 Master Governance & Pipeline Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase12_master_tests()
