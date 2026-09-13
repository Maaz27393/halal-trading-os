import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts import ExecutionIntent, TransactionType, OrderType, ProductType
from integrations.simulated_broker import SimulatedBrokerAdapter
from security.order_validator import OrderValidator
from security.gateway import PermissionGateway
from security.kill_switch import EmergencyKillSwitch, KillSwitchTriggeredError
from security.execution_gateway import ExecutionPolicyGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_kill_switch_tests():
    print("Initializing P3.9 - Kill-Switch & Circuit Breaker Tests...")

    assert LIVE_AUTO_EXECUTION is False, "Safety Violation: LIVE_AUTO_EXECUTION must remain False!"

    broker = SimulatedBrokerAdapter()
    broker.connect()

    validator = OrderValidator(max_capital_per_order=500000.0)
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("strategy_agent", "EXECUTE")
    
    kill_switch = EmergencyKillSwitch()

    policy_gateway = ExecutionPolicyGateway(
        broker=broker,
        validator=validator,
        permission_gateway=perm_gateway,
        kill_switch=kill_switch
    )

    intent = ExecutionIntent(
        source_provider="strategy_agent",
        strategy_id="TEST_STRAT",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=10,
        stop_loss=2800.0,
        target=2950.0,
        idempotency_key="KILL_SWITCH_TEST_001"
    )

    market_price = 2850.0

    # 1. Verify normal execution works before trip
    response = policy_gateway.execute(intent, market_price, caller_role="strategy_agent")
    assert response.status == "COMPLETE"
    print("Normal execution verified before kill-switch trip.")

    # 2. Trip the Emergency Kill-Switch
    kill_switch.trip(reason="Simulated High Slippage / API Flood Anomaly")
    assert kill_switch.is_tripped is True
    print(f"Kill-Switch Tripped Successfully. Reason: {kill_switch.trip_reason}")

    # 3. Attempt execution while kill-switch is active (must be blocked)
    intent_trip = ExecutionIntent(
        source_provider="strategy_agent",
        strategy_id="TEST_STRAT",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=10,
        stop_loss=2800.0,
        target=2950.0,
        idempotency_key="KILL_SWITCH_TEST_002"
    )

    try:
        policy_gateway.execute(intent_trip, market_price, caller_role="strategy_agent")
        raise AssertionError("Security Failure: Execution succeeded while kill-switch was tripped!")
    except KillSwitchTriggeredError as e:
        print(f"Kill-Switch Successfully Blocked Order Dispatch: {e}")

    # 4. Reset Kill-Switch with valid admin token
    kill_switch.reset(authorization_token="ADMIN_OVERRIDE_RESET_2026")
    assert kill_switch.is_tripped is False
    print("Kill-Switch successfully reset.")

    # 5. Verify execution works again after reset
    intent_post_reset = ExecutionIntent(
        source_provider="strategy_agent",
        strategy_id="TEST_STRAT",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=10,
        stop_loss=2800.0,
        target=2950.0,
        idempotency_key="KILL_SWITCH_TEST_003"
    )
    response_reset = policy_gateway.execute(intent_post_reset, market_price, caller_role="strategy_agent")
    assert response_reset.status == "COMPLETE"
    print("Post-reset execution verified successfully.")

    broker.disconnect()
    print("P3.9 Kill-Switch & Circuit Breaker Tests Passed Successfully!")

if __name__ == "__main__":
    run_kill_switch_tests()