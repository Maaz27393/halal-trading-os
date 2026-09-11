from enum import Enum
from typing import Dict, Any, List, Optional
import time

class OrderState(Enum):
    CREATED = "CREATED"
    PRECHECK_PASSED = "PRECHECK_PASSED"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class ExecutionOrder:
    def __init__(self, order_id: str, ticker: str, side: str, qty: int, limit_price: float, max_slippage_pct: float = 0.5):
        self.order_id = order_id
        self.ticker = ticker
        self.side = side.upper() # BUY or SELL
        self.qty = qty
        self.limit_price = limit_price
        self.max_slippage_pct = max_slippage_pct
        self.filled_qty = 0
        self.fill_price = 0.0
        self.state = OrderState.CREATED
        self.history: List[Dict[str, Any]] = []
        self._record_state_change(OrderState.CREATED, "Order object initialized.")

    def _record_state_change(self, new_state: OrderState, reason: str):
        self.state = new_state
        self.history.append({
            "state": new_state.value,
            "reason": reason,
            "timestamp": time.time()
        })

    def pass_precheck(self, audit_reason: str = "Pre-flight audit approved"):
        if self.state != OrderState.CREATED:
            raise ValueError(f"Cannot pass precheck from state {self.state}")
        self._record_state_change(OrderState.PRECHECK_PASSED, audit_reason)

    def submit_to_broker(self, broker_ref: str):
        if self.state != OrderState.PRECHECK_PASSED:
            raise ValueError(f"Cannot submit order to broker from state {self.state}")
        self._record_state_change(OrderState.SUBMITTED, f"Submitted to broker with ref: {broker_ref}")

    def execute_fill(self, execution_price: float, qty: int):
        if self.state not in [OrderState.SUBMITTED, OrderState.PARTIALLY_FILLED]:
            raise ValueError(f"Cannot fill order in state {self.state}")

        # Check slippage bounds
        slippage_pct = ((execution_price - self.limit_price) / self.limit_price) * 100.0 if self.side == "BUY" else ((self.limit_price - execution_price) / self.limit_price) * 100.0
        
        if slippage_pct > self.max_slippage_pct:
            self._record_state_change(OrderState.REJECTED, f"Slippage violation: {slippage_pct:.2f}% exceeds max allowed {self.max_slippage_pct}%")
            return False

        self.filled_qty += qty
        self.fill_price = execution_price

        if self.filled_qty >= self.qty:
            self._record_state_change(OrderState.FILLED, f"Filled at {execution_price} (Slippage: {slippage_pct:.2f}%)")
        else:
            self._record_state_change(OrderState.PARTIALLY_FILLED, f"Partial fill: {self.filled_qty}/{self.qty} at {execution_price}")
        return True

    def cancel(self, reason: str):
        if self.state in [OrderState.FILLED, OrderState.REJECTED, OrderState.CANCELLED]:
            raise ValueError(f"Cannot cancel terminal order state {self.state}")
        self._record_state_change(OrderState.CANCELLED, reason)

    def reject(self, reason: str):
        if self.state in [OrderState.FILLED, OrderState.CANCELLED]:
            raise ValueError(f"Cannot reject finalized order in state {self.state}")
        self._record_state_change(OrderState.REJECTED, reason)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "ticker": self.ticker,
            "side": self.side,
            "qty": self.qty,
            "filled_qty": self.filled_qty,
            "limit_price": self.limit_price,
            "fill_price": self.fill_price,
            "state": self.state.value,
            "history_steps": len(self.history)
        }
