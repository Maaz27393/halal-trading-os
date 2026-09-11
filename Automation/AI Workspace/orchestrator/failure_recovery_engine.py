import time
from typing import Dict, Any, List
from execution_state_machine import ExecutionOrder, OrderState
from position_state_engine import PositionStateEngine

class FailureRecoveryEngine:
    """
    Phase 9F: Failure Recovery & Edge Case Handling
    Manages order timeouts, stale request purges, partial fill cleanup,
    and portfolio state integrity during execution failures.
    """
    def __init__(self, stale_timeout_seconds: float = 30.0):
        self.stale_timeout_seconds = stale_timeout_seconds

    def process_stale_orders(self, orders: List[ExecutionOrder], current_time: float = None) -> List[Dict[str, Any]]:
        now = current_time or time.time()
        recovery_log = []

        for order in orders:
            if order.state == OrderState.SUBMITTED:
                age = now - order.created_at
                if age > self.stale_timeout_seconds:
                    success = order.cancel(reason=f"Execution timeout: order exceeded {self.stale_timeout_seconds}s limit")
                    recovery_log.append({
                        "order_id": order.order_id,
                        "ticker": order.ticker,
                        "action": "AUTO_CANCELLED",
                        "reason": f"Age {age:.1f}s exceeded timeout threshold {self.stale_timeout_seconds}s",
                        "success": success
                    })

            elif order.state == OrderState.PARTIALLY_FILLED:
                age = now - order.created_at
                if age > self.stale_timeout_seconds:
                    success = order.cancel(reason=f"Partial fill timeout: cancelling residual unfilled quantity ({order.qty - order.filled_qty})")
                    recovery_log.append({
                        "order_id": order.order_id,
                        "ticker": order.ticker,
                        "action": "PARTIAL_RESIDUAL_CANCELLED",
                        "retained_filled_qty": order.filled_qty,
                        "cancelled_qty": order.qty - order.filled_qty,
                        "success": success
                    })

        return recovery_log

    def handle_unexpected_rejection(self, order: ExecutionOrder, position_engine: PositionStateEngine, reason: str) -> Dict[str, Any]:
        """Safely isolates rejected orders and guarantees no position leak or capital lockup."""
        success = order.reject(reason=f"Recovery Interceptor: {reason}")
        
        ghost_position = position_engine.positions.get(order.ticker)
        has_ghost = ghost_position is not None and order.filled_qty == 0

        if has_ghost:
            position_engine.positions.pop(order.ticker, None)

        return {
            "order_id": order.order_id,
            "state": order.state.value,
            "rejection_handled": success,
            "ghost_position_purged": has_ghost
        }
