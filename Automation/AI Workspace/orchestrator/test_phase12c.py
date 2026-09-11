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

def run_phase12c_tests():
    print("=== STARTING PHASE 12C: SHADOW EXECUTION ENGINE & TELEMETRY TESTS ===")

    broker = BrokerSessionManager(broker_name="Shoonya")
    broker.authenticate("MOCK_KEY", "USER123", "123456")

    auditor = LiveReadinessAuditor(broker_session=broker, max_risk_per_trade_pct=1.0, max_trades_per_day=2)
    harness = FailureStressHarness(max_allowed_slippage_pct=0.5)
    engine = ShadowExecutionEngine(readiness_auditor=auditor, stress_harness=harness)

    account_state = {
        "available_cash": 100000.0,
        "invested_value": 0.0,
        "trades_today_count": 0
    }

    # Test 1: Valid Signal -> Simulated Shadow Fill
    valid_signal = {
        "trading_symbol": "TATASTEEL-EQ",
        "action": "BUY",
        "quantity": 50,
        "trigger_price": 150.0,
        "risk_amount": 500.0,
        "risk_reward_ratio": 2.0,
        "product_type": "DELIVERY"
    }
    res1 = engine.execute_shadow_trade(valid_signal, market_price=150.1, account_state=account_state)
    assert res1["status"] == "FILLED_SHADOW"
    assert res1["fill"]["shadow_order_id"].startswith("SHADOW_")
    print("[PASS] Test 1 | Valid Signal Shadow Execution & Simulated Fill Verified")

    # Test 2: Invalid Risk Invariant (Unauthorized Product Type F&O) -> Shadow Rejection
    invalid_risk_signal = {
        "trading_symbol": "NIFTY-FUT",
        "action": "BUY",
        "quantity": 50,
        "trigger_price": 22000.0,
        "risk_amount": 500.0,
        "risk_reward_ratio": 2.0,
        "product_type": "FUTURES"
    }
    res2 = engine.execute_shadow_trade(invalid_risk_signal, market_price=22000.0, account_state=account_state)
    assert res2["status"] == "REJECTED_RISK_INVARIANT"
    assert "UNAUTHORIZED_PRODUCT_TYPE" in res2["reason"]
    print("[PASS] Test 2 | Risk Invariant Gate Interception in Shadow Engine Verified")

    # Test 3: Slippage Surge Abort -> Shadow Abort
    slippage_signal = {
        "trading_symbol": "INFY-EQ",
        "action": "BUY",
        "quantity": 10,
        "trigger_price": 1500.0,
        "risk_amount": 400.0,
        "risk_reward_ratio": 1.8,
        "product_type": "DELIVERY"
    }
    res3 = engine.execute_shadow_trade(slippage_signal, market_price=1520.0, account_state=account_state)
    assert res3["status"] == "ABORTED_SLIPPAGE_SURGE"
    assert "SLIPPAGE_SURGE_EXCEEDED" in res3["reason"]
    print("[PASS] Test 3 | Post-Signal Slippage Surge Shadow Abort Verified")

    # Test 4: Real-Time Telemetry Summary Aggregation
    summary = engine.get_telemetry_summary()
    assert summary["total_signals_processed"] == 3
    assert summary["shadow_orders_filled"] == 1
    assert summary["orders_rejected_or_aborted"] == 2
    assert summary["avg_latency_ms"] >= 0.0
    print("[PASS] Test 4 | Telemetry Metrics & Latency Summary Aggregation Verified")

    print("\nPhase 12C Shadow Execution Engine & Telemetry Benchmark: 4/4 Passed")

if __name__ == "__main__":
    run_phase12c_tests()
