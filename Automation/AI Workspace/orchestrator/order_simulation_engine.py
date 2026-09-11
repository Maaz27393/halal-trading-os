from typing import Dict, Any, Optional
from execution_state_machine import ExecutionOrder, OrderState

class OrderSimulationEngine:
    """
    Phase 9D: Order Simulation Engine
    Simulates fill dynamics against market depth, bid/ask spreads, and volume constraints.
    Injects fills into ExecutionOrder objects while obeying order limit boundaries.
    """
    def __init__(self, default_slippage_pct: float = 0.05):
        self.default_slippage_pct = default_slippage_pct

    def simulate_fill(self, order: ExecutionOrder, market_snap: Dict[str, Any]) -> Dict[str, Any]:
        if order.state != OrderState.SUBMITTED:
            return {"status": "SKIPPED", "reason": f"Order in invalid state {order.state} for simulation"}

        ask_price = float(market_snap.get("ask", market_snap.get("close", 0.0)))
        bid_price = float(market_snap.get("bid", market_snap.get("close", 0.0)))
        available_vol = int(market_snap.get("volume", 0))

        if order.side == "BUY":
            # For BUY, order fills if ask price <= limit price + small tolerance
            if ask_price > order.limit_price * 1.005:
                return {"status": "UNFILLED", "reason": f"Ask price {ask_price} above limit boundary {order.limit_price}"}

            # Calculate actual fill price with simulated slippage
            fill_price = round(ask_price * (1.0 + (self.default_slippage_pct / 100.0)), 2)
            fill_qty = min(order.qty - order.filled_qty, available_vol) if available_vol > 0 else order.qty

            if fill_qty <= 0:
                return {"status": "UNFILLED", "reason": "Zero volume available at price"}

            success = order.execute_fill(execution_price=fill_price, qty=fill_qty)
            return {
                "status": "FILLED" if order.state == OrderState.FILLED else ("PARTIALLY_FILLED" if success else "REJECTED"),
                "fill_price": fill_price,
                "fill_qty": fill_qty,
                "order_state": order.state.value
            }

        elif order.side == "SELL":
            if bid_price < order.limit_price * 0.995:
                return {"status": "UNFILLED", "reason": f"Bid price {bid_price} below limit boundary {order.limit_price}"}

            fill_price = round(bid_price * (1.0 - (self.default_slippage_pct / 100.0)), 2)
            fill_qty = min(order.qty - order.filled_qty, available_vol) if available_vol > 0 else order.qty

            if fill_qty <= 0:
                return {"status": "UNFILLED", "reason": "Zero volume available at price"}

            success = order.execute_fill(execution_price=fill_price, qty=fill_qty)
            return {
                "status": "FILLED" if order.state == OrderState.FILLED else ("PARTIALLY_FILLED" if success else "REJECTED"),
                "fill_price": fill_price,
                "fill_qty": fill_qty,
                "order_state": order.state.value
            }

        return {"status": "ERROR", "reason": f"Unsupported order side '{order.side}'"}
