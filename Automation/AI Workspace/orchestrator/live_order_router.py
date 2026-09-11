import time
from typing import Dict, Any, Optional

class LiveOrderRouter:
    """
    Phase 11C: Live Order Router & Execution State Machine
    Routes risk-checked orders to the broker, manages life-cycle state transitions,
    and enforces timeout cancellations on unexecuted orders.
    """
    VALID_STATES = {"SUBMITTED", "PENDING", "PARTIALLY_FILLED", "FILLED", "CANCELLED", "REJECTED"}

    def __init__(self, safety_interlock, broker_session):
        self.interlock = safety_interlock
        self.broker = broker_session
        self.orders: Dict[str, Dict[str, Any]] = {}

    def route_and_submit_order(self, order_request: Dict[str, Any], ltp: float, is_halal: bool, current_daily_loss: float = 0.0) -> Dict[str, Any]:
        """Validates pre-trade risk, formats order payload, and registers order state."""
        # 1. Safety Interlock Validation
        risk_res = self.interlock.validate_order(order_request, ltp, is_halal, current_daily_loss)
        if not risk_res["approved"]:
            return {"status": "REJECTED", "reason": risk_res["reason"], "order_id": None}

        # 2. Session Validation & Payload Formatting
        if not self.broker.is_session_valid():
            return {"status": "REJECTED", "reason": "BROKER_SESSION_INVALID", "order_id": None}

        order_id = f"ORD_{int(time.time() * 1000)}"
        formatted_payload = self.broker.format_live_order_payload(
            ticker=order_request["trading_symbol"],
            side=order_request["transaction_type"],
            qty=order_request["quantity"],
            order_type=order_request.get("price_type", "LIMIT"),
            price=order_request.get("price", ltp)
        )

        # 3. Store Order Lifecycle State
        self.orders[order_id] = {
            "order_id": order_id,
            "payload": formatted_payload,
            "state": "SUBMITTED",
            "filled_qty": 0,
            "total_qty": order_request["quantity"],
            "avg_fill_price": 0.0,
            "updated_at": int(time.time())
        }
        return {"status": "SUBMITTED", "order_id": order_id, "payload": formatted_payload}

    def update_order_state(self, order_id: str, new_state: str, filled_qty: int = 0, fill_price: float = 0.0) -> Dict[str, Any]:
        """Transitions order state through the lifecycle."""
        if order_id not in self.orders:
            return {"error": "Order ID not found"}
        
        state_upper = new_state.upper()
        if state_upper not in self.VALID_STATES:
            return {"error": f"Invalid state {state_upper}"}

        order = self.orders[order_id]
        order["state"] = state_upper
        order["updated_at"] = int(time.time())

        if filled_qty > 0:
            order["filled_qty"] = filled_qty
            order["avg_fill_price"] = fill_price

        if order["filled_qty"] >= order["total_qty"]:
            order["state"] = "FILLED"

        return order

    def handle_execution_timeout(self, order_id: str, max_age_seconds: int = 30) -> Dict[str, Any]:
        """Cancels orders that remain unfilled beyond the timeout window."""
        if order_id not in self.orders:
            return {"action": "NONE", "reason": "ORDER_NOT_FOUND"}

        order = self.orders[order_id]
        if order["state"] in ["FILLED", "CANCELLED", "REJECTED"]:
            return {"action": "NONE", "reason": f"ORDER_ALREADY_{order['state']}"}

        age = int(time.time()) - order["updated_at"]
        if age >= max_age_seconds:
            order["state"] = "CANCELLED"
            order["updated_at"] = int(time.time())
            return {"action": "CANCELLED_DUE_TO_TIMEOUT", "order_id": order_id, "age_seconds": age}

        return {"action": "ACTIVE", "order_id": order_id, "age_seconds": age}
