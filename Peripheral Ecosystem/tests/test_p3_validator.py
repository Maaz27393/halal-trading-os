import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts import ExecutionIntent, TransactionType, OrderType, ProductType
from security.order_validator import OrderValidator, OrderValidationError

def run_validator_tests():
    print("Initializing P3.4 - Order Validation Layer Tests...")

    validator = OrderValidator(max_capital_per_order=200000.0)

    # Valid intent: Buy Reliance @ 2850, SL 2800, Target 2950
    valid_intent = ExecutionIntent(
        source_provider="strategy_engine",
        strategy_id="TEST_STRAT",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=50,
        stop_loss=2800.0,
        target=2950.0,
        idempotency_key="KEY_VALID_001"
    )

    market_price = 2850.0
    assert validator.validate_intent(valid_intent, market_price) is True
    print("Valid order intent passed successfully.")

    # Test 1: Idempotency Duplication Check
    try:
        validator.validate_intent(valid_intent, market_price)
        raise AssertionError("Idempotency failure: Duplicate key was accepted!")
    except OrderValidationError as e:
        print(f"Idempotency Guardrail Caught Duplicate Successfully: {e}")

    # Test 2: Capital Exposure Limit Violation (Order value exceeds 200k)
    large_intent = ExecutionIntent(
        source_provider="strategy_engine",
        strategy_id="TEST_STRAT",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=100,  # 100 * 2850 = 285,000 (> 200,000)
        stop_loss=2800.0,
        target=2950.0,
        idempotency_key="KEY_LARGE_002"
    )

    try:
        validator.validate_intent(large_intent, market_price)
        raise AssertionError("Capital limit failure: Oversized order was accepted!")
    except OrderValidationError as e:
        print(f"Capital Limit Guardrail Caught Excess Size Successfully: {e}")

    # Test 3: Invalid Stop-Loss for Buy Order (SL above market price)
    bad_sl_intent = ExecutionIntent(
        source_provider="strategy_engine",
        strategy_id="TEST_STRAT",
        symbol="RELIANCE",
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=10,
        stop_loss=2900.0,  # Invalid: SL is above market price 2850
        target=2950.0,
        idempotency_key="KEY_BAD_SL_003"
    )

    try:
        validator.validate_intent(bad_sl_intent, market_price)
        raise AssertionError("Stop-loss rule failure: Invalid SL was accepted!")
    except OrderValidationError as e:
        print(f"Risk Guardrail Caught Invalid Stop-Loss Successfully: {e}")

    print("P3.4 Order Validation Layer Tests Passed Successfully!")

if __name__ == "__main__":
    run_validator_tests()