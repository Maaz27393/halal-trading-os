import sys
import os
import concurrent.futures

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts import ExecutionIntent, TransactionType, OrderType, ProductType
from integrations.simulated_broker import SimulatedBrokerAdapter
from security.order_validator import OrderValidator, OrderValidationError
from security.gateway import PermissionGateway
from security.execution_gateway import ExecutionPolicyGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_broker_stress_tests():
    print("Initializing P3.7 - Broker & Execution Sandbox Stress Tests...")

    assert LIVE_AUTO_EXECUTION is False, "Safety Violation: LIVE_AUTO_EXECUTION must remain False!"

    broker = SimulatedBrokerAdapter()
    broker.connect()

    validator = OrderValidator(max_capital_per_order=500000.0)
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("stress_agent", "EXECUTE")

    policy_gateway = ExecutionPolicyGateway(
        broker=broker,
        validator=validator,
        permission_gateway=perm_gateway
    )

    market_price = 2850.0

    # Test 1: Concurrent Rapid-Fire Order Submissions
    print("Executing concurrent order dispatch stress test...")
    
    def dispatch_single_order(index: int):
        intent = ExecutionIntent(
            source_provider="stress_agent",
            strategy_id="STRESS_TEST_V1",
            symbol="RELIANCE",
            transaction_type=TransactionType.BUY,
            order_type=OrderType.MARKET,
            product=ProductType.MIS,
            quantity=10,
            stop_loss=2800.0,
            target=2950.0,
            idempotency_key=f"STRESS_KEY_{index}"
        )
        return policy_gateway.execute(intent, market_price, caller_role="stress_agent")

    # Dispatch 20 concurrent orders
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(dispatch_single_order, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    print(f"Successfully processed {len(results)} concurrent simulated orders.")
    assert len(results) == 20
    for res in results:
        assert res.status == "COMPLETE"
        assert res.broker_order_id.startswith("SIM_")

    # Test 2: Idempotency Re-submission Attack Test
    print("Testing idempotency collision protection under stress...")
    duplicate_intent = ExecutionIntent(
        source_provider="stress_agent",
        strategy_id="STRESS_TEST_V1",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=10,
        stop_loss=2800.0,
        target=2950.0,
        idempotency_key="STRESS_KEY_0"  # Already used in concurrent test
    )

    try:
        policy_gateway.execute(duplicate_intent, market_price, caller_role="stress_agent")
        raise AssertionError("Idempotency failure: Duplicate idempotency key was allowed through gateway!")
    except OrderValidationError as e:
        print(f"Idempotency Firewall Successfully Blocked Duplicate Key: {e}")

    broker.disconnect()
    print("P3.7 Broker & Execution Sandbox Stress Tests Passed Successfully!")

if __name__ == "__main__":
    run_broker_stress_tests()