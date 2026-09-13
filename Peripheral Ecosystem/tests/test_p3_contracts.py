import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts import ExecutionIntent, OrderResponse, TransactionType, OrderType, ProductType

def run_contract_tests():
    print("Initializing P3.1 - Execution & Order Contracts Validation...")

    intent = ExecutionIntent(
        source_provider="strategy_engine",
        strategy_id="EMA_CROSSOVER_V1",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=50,
        stop_loss=2820.0,
        target=2910.0,
        idempotency_key="idempotency_uuid_998877"
    )

    response = OrderResponse(
        source_provider="kite_broker",
        broker_order_id="260913000012345",
        status="PENDING",
        message="Order queued in simulation mode (LIVE_AUTO_EXECUTION=FALSE)",
        filled_quantity=0
    )

    assert intent.symbol == "RELIANCE"
    assert response.status == "PENDING"
    print(f"Execution Intent Canonicalized: {intent.model_dump()}")
    print(f"Order Response Canonicalized: {response.model_dump()}")
    print("P3.1 Execution Contracts Validation Passed Successfully!")

if __name__ == "__main__":
    run_contract_tests()