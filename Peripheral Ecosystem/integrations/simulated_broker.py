import logging
import uuid
from typing import Any, Dict, List, Optional
from connectors.broker_base import BaseBrokerConnector, LIVE_AUTO_EXECUTION
from contracts import ExecutionIntent, OrderResponse

logger = logging.getLogger("SimulatedBrokerAdapter")

class SimulatedBrokerAdapter(BaseBrokerConnector):
    """
    Paper-trading and shadow-dispatch broker adapter.
    Intercepts execution intents and simulates order matching, margin checks, 
    and responses locally while keeping LIVE_AUTO_EXECUTION strictly disabled.
    """

    def __init__(self):
        super().__init__(broker_name="simulated_kite_broker")
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.ledger_balance = 500000.0  # 5 Lakhs simulated capital

    def connect(self) -> bool:
        self.is_connected = True
        logger.info("Connected to Simulated Broker Sandbox successfully.")
        return True

    def get_account_margin(self) -> Dict[str, Any]:
        return {
            "available_cash": self.ledger_balance,
            "utilized_margin": 0.0,
            "net": self.ledger_balance
        }

    def place_order(self, intent: ExecutionIntent) -> OrderResponse:
        # Safety enforcement
        if LIVE_AUTO_EXECUTION:
            raise PermissionError("FATAL: Live auto-execution is disabled by system policy.")

        logger.info(f"[PAPER/SHADOW MODE] Processing Execution Intent for {intent.symbol} [{intent.transaction_type}] quantity={intent.quantity}")

        # Simulate order ID generation
        simulated_order_id = f"SIM_{uuid.uuid4().hex[:10].upper()}"
        
        order_record = {
            "broker_order_id": simulated_order_id,
            "strategy_id": intent.strategy_id,
            "symbol": intent.symbol,
            "transaction_type": intent.transaction_type,
            "quantity": intent.quantity,
            "order_type": intent.order_type,
            "status": "COMPLETE" if intent.order_type == "MARKET" else "OPEN",
            "message": "Simulated order executed successfully in paper mode.",
            "average_price": 2850.5 if intent.price == 0.0 else intent.price
        }

        self.active_orders[simulated_order_id] = order_record

        return OrderResponse(
            source_provider=self.broker_name,
            broker_order_id=simulated_order_id,
            status=order_record["status"],
            message=order_record["message"],
            filled_quantity=intent.quantity if order_record["status"] == "COMPLETE" else 0,
            average_price=order_record["average_price"]
        )

    def cancel_order(self, broker_order_id: str) -> OrderResponse:
        if broker_order_id not in self.active_orders:
            return OrderResponse(
                source_provider=self.broker_name,
                broker_order_id=broker_order_id,
                status="REJECTED",
                message="Order ID not found for cancellation."
            )
        
        self.active_orders[broker_order_id]["status"] = "CANCELLED"
        return OrderResponse(
            source_provider=self.broker_name,
            broker_order_id=broker_order_id,
            status="CANCELLED",
            message="Order successfully cancelled in simulation."
        )

    def get_order_status(self, broker_order_id: str) -> OrderResponse:
        record = self.active_orders.get(broker_order_id)
        if not record:
            return OrderResponse(
                source_provider=self.broker_name,
                broker_order_id=broker_order_id,
                status="NOT_FOUND",
                message="Order ID does not exist."
            )

        return OrderResponse(
            source_provider=self.broker_name,
            broker_order_id=broker_order_id,
            status=record["status"],
            message=record["message"],
            filled_quantity=record["quantity"] if record["status"] == "COMPLETE" else 0,
            average_price=record["average_price"]
        )

    def disconnect(self) -> bool:
        self.is_connected = False
        logger.info("Disconnected from Simulated Broker Sandbox.")
        return True