import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts import ExecutionIntent, TransactionType, OrderType, ProductType
from integrations.kite_adapter import KiteBrokerAdapter
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_kite_tests():
    print("Initializing P3.3 - Kite Adapter & Safety Boundary Tests...")

    assert LIVE_AUTO_EXECUTION is False, "Safety Violation: LIVE_AUTO_EXECUTION must remain False!"
    
    adapter = KiteBrokerAdapter(api_key="test_kite_key_123")
    assert adapter.connect() is True
    assert adapter.is_connected is True

    margins = adapter.get_account_margin()
    print(f"Kite Sandbox Margins Fetched: {margins}")
    assert margins["available_cash"] == 1000000.0

    # Verify that attempting to place an order via Kite directly throws PermissionError due to guardrail
    intent = ExecutionIntent(
        source_provider="strategy_engine",
        strategy_id="TEST_STRATEGY",
        symbol="TATASTEEL",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=10,
        idempotency_key="KITE_TEST_KEY"
    )

    try:
        adapter.place_order(intent)
        raise AssertionError("Security Failure: Live order placement succeeded when LIVE_AUTO_EXECUTION=False!")
    except PermissionError as e:
        print(f"Safety Guardrail Caught Live Order Attempt Successfully: {e}")

    adapter.disconnect()
    assert adapter.is_connected is False
    print("P3.3 Kite Adapter & Safety Boundary Tests Passed Successfully!")

if __name__ == "__main__":
    run_kite_tests()