import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts import ExecutionIntent, TransactionType, OrderType, ProductType
from integrations.simulated_broker import SimulatedBrokerAdapter
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_broker_tests():
    print("Initializing P3.2 - Broker Adapter & Paper Dispatch Tests...")

    # Verify safety guardrail default
    assert LIVE_AUTO_EXECUTION is False, "Safety violation: LIVE_AUTO_EXECUTION must be False by default!"
    print("Safety Guardrail Verified: LIVE_AUTO_EXECUTION = False")

    broker = SimulatedBrokerAdapter()
    broker.connect()

    # Check account margin
    margin = broker.get_account_margin()
    print(f"Account Margin Status: {margin}")
    assert margin["available_cash"] > 0

    # Construct test execution intent
    intent = ExecutionIntent(
        source_provider="strategy_engine",
        strategy_id="EMA_CROSSOVER_V1",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=25,
        stop_loss=2810.0,
        target=2920.0,
        idempotency_key="TEST_KEY_445566"
    )

    # Dispatch order in paper mode
    response = broker.place_order(intent)
    print(f"Order Dispatch Response: {response.model_dump()}")
    assert response.status == "COMPLETE"
    assert response.broker_order_id.startswith("SIM_")

    # Verify status lookup
    status_response = broker.get_order_status(response.broker_order_id)
    assert status_response.status == "COMPLETE"
    print(f"Order Status Verified: {status_response.status}")

    broker.disconnect()
    print("P3.2 Broker Adapter & Paper Dispatch Tests Passed Successfully!")

if __name__ == "__main__":
    run_broker_tests()