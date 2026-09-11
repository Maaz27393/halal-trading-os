from typing import Dict, Any, Optional
from execution_state_machine import ExecutionOrder, OrderState
from position_state_engine import PositionStateEngine

class ExecutionReconciler:
    """
    Phase 9E: Execution Reconciliation Suite
    Audits order intent against execution results, calculates exact slippage impact,
    and reconciles executed trades into the Position State Engine.
    """
    def reconcile(self, order: ExecutionOrder, position_engine: PositionStateEngine) -> Dict[str, Any]:
        audit_report = {
            "order_id": order.order_id,
            "ticker": order.ticker,
            "side": order.side,
            "requested_qty": order.qty,
            "filled_qty": order.filled_qty,
            "requested_limit_price": order.limit_price,
            "actual_fill_price": order.fill_price,
            "status": "UNMATCHED",
            "slippage_pct": 0.0,
            "discrepancy": None
        }

        # Terminal state: REJECTED or CANCELLED
        if order.state in [OrderState.REJECTED, OrderState.CANCELLED]:
            audit_report["status"] = "TERMINATED_WITHOUT_FILL"
            audit_report["discrepancy"] = f"Order ended in state {order.state.value}"
            return audit_report

        # Active state: SUBMITTED without fills
        if order.state == OrderState.SUBMITTED and order.filled_qty == 0:
            audit_report["status"] = "PENDING_FILL"
            return audit_report

        # Calculate Slippage
        if order.fill_price > 0:
            if order.side == "BUY":
                audit_report["slippage_pct"] = round(((order.fill_price - order.limit_price) / order.limit_price) * 100.0, 4)
            else:
                audit_report["slippage_pct"] = round(((order.limit_price - order.fill_price) / order.limit_price) * 100.0, 4)

        # Reconcile into Position Engine if FILLED or PARTIALLY_FILLED
        if order.state in [OrderState.FILLED, OrderState.PARTIALLY_FILLED]:
            if order.side == "BUY":
                # Compute default Stop Loss & Target if not explicitly passed
                stop_loss = round(order.fill_price * 0.97, 2) # Default 3% SL
                target_price = round(order.fill_price * 1.05, 2) # Default 5% Target

                pos_res = position_engine.open_position(
                    ticker=order.ticker,
                    qty=order.filled_qty,
                    entry_price=order.fill_price,
                    stop_loss=stop_loss,
                    target_price=target_price
                )

                if pos_res["success"]:
                    audit_report["status"] = "RECONCILED_MATCH" if order.state == OrderState.FILLED else "RECONCILED_PARTIAL"
                else:
                    audit_report["status"] = "POSITION_SYNC_ERROR"
                    audit_report["discrepancy"] = pos_res["reason"]

            elif order.side == "SELL":
                close_res = position_engine.close_position(ticker=order.ticker, exit_price=order.fill_price)
                if close_res["success"]:
                    audit_report["status"] = "RECONCILED_MATCH"
                    audit_report["realized_pnl"] = close_res["realized_pnl"]
                else:
                    audit_report["status"] = "POSITION_SYNC_ERROR"
                    audit_report["discrepancy"] = close_res["reason"]

        return audit_report
