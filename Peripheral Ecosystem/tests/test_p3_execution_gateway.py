import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts import ExecutionIntent, TransactionType, OrderType, ProductType
from security.execution_gateway import ExecutionPolicyGateway
from security.order_validator import OrderValidator, OrderValidationError
from security.gateway import PermissionGateway
from integrations.simulated_broker import SimulatedBrokerAdapter
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_gateway_tests():
    print("Initializing P3.5 - Execution Policy Gateway Tests...")

    assert LIVE_AUTO_EXECUTION is False, "Safety Violation: LIVE_AUTO_EXECUTION must be False!"

    # Setup components
    broker = SimulatedBrokerAdapter()
    broker.connect()

    validator = OrderValidator(max_capital_per_order=200000.0)
    perm_gateway = PermissionGateway()
    # Register default execution role permissions
    perm_gateway.grant_permission("strategy_engine", "EXECUTE")

    policy_gateway = ExecutionPolicyGateway(
        broker=broker,
        validator=validator,
        permission_gateway=perm_gateway
    )

    # Construct valid execution intent
    intent = ExecutionIntent(
        source_provider="strategy_engine",
        strategy_id="EMA_CROSSOVER_V1",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=30,
        stop_loss=2810.0,
        target=2920.0,
        idempotency_key="GATEWAY_TEST_KEY_999"
    )

    market_price = 2850.0

    # Execute via Gateway
    response = policy_gateway.execute(intent, market_price, caller_role="strategy_engine")
    print(f"Gateway Execution Response: {response.model_dump()}")

    assert response.status == "COMPLETE"
    assert response.broker_order_id.startswith("SIM_")

    broker.disconnect()
    print("P3.5 Execution Policy Gateway Tests Passed Successfully!")

if __name__ == "__main__":
    run_gateway_tests()