import time
from enum import Enum
from typing import Dict, Any, Optional

class OrderState(Enum):
    CREATED = "CREATED"
    PRECHECK_PASSED = "PRECHECK_PASSED"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class ExecutionOrder:
    """
    Phase 9A: Execution State Machine Order Entity
    Tracks full lifecycle from creation -> precheck -> submission -> fill / cancellation / rejection.
    """
    def __init__(self, order_id: str, ticker: str, side: str, qty: int, limit_price: float, max_slippage_pct: float = 0.5):
        self.order_id = order_id
        self.ticker = ticker.upper()
        self.side = side.upper()
        self.qty = qty
        self.limit_price = limit_price
        self.max_slippage_pct = max_slippage_pct
        self.state = OrderState.CREATED
        self.broker_id = None
        self.filled_qty = 0
        self.fill_price = 0.0
        self.created_at = time.time()
        self.rejection_reason = None

    def pass_precheck(self) -> bool:
        if self.state == OrderState.CREATED:
            self.state = OrderState.PRECHECK_PASSED
            return True
        return False

    def submit_to_broker(self, broker_id: str) -> bool:
        if self.state == OrderState.PRECHECK_PASSED:
            self.broker_id = broker_id
            self.state = OrderState.SUBMITTED
            return True
        return False

    def execute_fill(self, execution_price: float, qty: int) -> bool:
        if self.state not in [OrderState.SUBMITTED, OrderState.PARTIALLY_FILLED]:
            return False

        if self.side == "BUY":
            slippage_pct = ((execution_price - self.limit_price) / self.limit_price) * 100.0
        else:
            slippage_pct = ((self.limit_price - execution_price) / self.limit_price) * 100.0

        if slippage_pct > self.max_slippage_pct:
            self.reject(f"Slippage limit violated: {slippage_pct:.2f}% > max {self.max_slippage_pct}%")
            return False

        new_total_filled = self.filled_qty + qty
        if new_total_filled > self.qty:
            return False

        current_total = self.filled_qty * self.fill_price
        new_fill_total = current_total + (qty * execution_price)
        self.fill_price = round(new_fill_total / new_total_filled, 2)
        self.filled_qty = new_total_filled

        if self.filled_qty == self.qty:
            self.state = OrderState.FILLED
        else:
            self.state = OrderState.PARTIALLY_FILLED
        return True

    def cancel(self, reason: str = "") -> bool:
        if self.state in [OrderState.SUBMITTED, OrderState.PARTIALLY_FILLED]:
            self.state = OrderState.CANCELLED
            self.rejection_reason = reason
            return True
        return False

    def reject(self, reason: str = "") -> bool:
        if self.state in [OrderState.CREATED, OrderState.PRECHECK_PASSED, OrderState.SUBMITTED]:
            self.state = OrderState.REJECTED
            self.rejection_reason = reason
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "ticker": self.ticker,
            "side": self.side,
            "qty": self.qty,
            "limit_price": self.limit_price,
            "state": self.state.value,
            "broker_id": self.broker_id,
            "filled_qty": self.filled_qty,
            "fill_price": self.fill_price,
            "rejection_reason": self.rejection_reason
        }
