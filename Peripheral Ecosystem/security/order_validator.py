import logging
from typing import Dict, Any, Optional
from contracts import ExecutionIntent, TransactionType

logger = logging.getLogger("OrderValidator")

class OrderValidationError(ValueError):
    """Raised when an execution intent violates pre-trade risk or compliance rules."""
    pass

class OrderValidator:
    """
    Pre-trade validation engine enforcing lot sizes, capital limits, 
    risk parameters, and idempotency checks.
    """

    def __init__(self, max_capital_per_order: float = 200000.0, enforced_lot_sizes: Optional[Dict[str, int]] = None):
        self.max_capital_per_order = max_capital_per_order
        self.enforced_lot_sizes = enforced_lot_sizes or {
            "RELIANCE": 1,
            "NIFTY": 25,
            "BANKNIFTY": 15,
            "TATASTEEL": 1
        }
        self._processed_idempotency_keys = set()
        logger.info("OrderValidator initialized with strict pre-trade safety rules.")

    def validate_intent(self, intent: ExecutionIntent, current_market_price: float) -> bool:
        """
        Validate an incoming ExecutionIntent against all risk and compliance criteria.
        Raises OrderValidationError if any check fails.
        """
        logger.info(f"Validating ExecutionIntent for {intent.symbol} [Strategy: {intent.strategy_id}]...")

        # 1. Idempotency Check
        if intent.idempotency_key in self._processed_idempotency_keys:
            raise OrderValidationError(f"Duplicate order blocked by idempotency key: {intent.idempotency_key}")

        # 2. Quantity & Lot Size Validation
        standard_lot = self.enforced_lot_sizes.get(intent.symbol, 1)
        if intent.quantity % standard_lot != 0:
            raise OrderValidationError(
                f"Quantity {intent.quantity} for {intent.symbol} violates lot size rules "
                f"(must be a multiple of {standard_lot})."
            )

        # 3. Capital & Exposure Check
        estimated_value = intent.quantity * (intent.price if intent.price > 0 else current_market_price)
        if estimated_value > self.max_capital_per_order:
            raise OrderValidationError(
                f"Order value ₹{estimated_value:,.2f} exceeds maximum allowed capital per order "
                f"limit of ₹{self.max_capital_per_order:,.2f}."
            )

        # 4. Stop-Loss & Target Logic Check
        if intent.transaction_type == TransactionType.BUY:
            if intent.stop_loss > 0 and intent.stop_loss >= current_market_price:
                raise OrderValidationError("Invalid Buy Stop-Loss: Stop-loss must be below current market price.")
            if intent.target > 0 and intent.target <= current_market_price:
                raise OrderValidationError("Invalid Buy Target: Target must be above current market price.")
        elif intent.transaction_type == TransactionType.SELL:
            if intent.stop_loss > 0 and intent.stop_loss <= current_market_price:
                raise OrderValidationError("Invalid Sell Stop-Loss: Stop-loss must be above current market price.")
            if intent.target > 0 and intent.target >= current_market_price:
                raise OrderValidationError("Invalid Sell Target: Target must be below current market price.")

        # Mark idempotency key as seen
        self._processed_idempotency_keys.add(intent.idempotency_key)
        logger.info(f"ExecutionIntent for {intent.symbol} successfully validated.")
        return True