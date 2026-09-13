import abc
import logging
from typing import Any, Dict, List, Optional
from contracts import ExecutionIntent, OrderResponse

logger = logging.getLogger("BrokerBaseConnector")

# IMMUTABLE SAFETY GUARDRAIL
LIVE_AUTO_EXECUTION = False

class BaseBrokerConnector(abc.ABC):
    """
    Abstract base class for all broker execution adapters.
    Enforces strict safety controls, paper-trading simulation by default,
    and standardized order lifecycle methods.
    """

    def __init__(self, broker_name: str):
        self.broker_name = broker_name
        self.is_connected = False
        logger.info(f"Initialized Broker Connector: {self.broker_name} [LIVE_AUTO_EXECUTION={LIVE_AUTO_EXECUTION}]")

    @abc.abstractmethod
    def connect(self) -> bool:
        """Establish session connection with the broker API."""
        pass

    @abc.abstractmethod
    def get_account_margin(self) -> Dict[str, Any]:
        """Fetch available margin and fund limits."""
        pass

    @abc.abstractmethod
    def place_order(self, intent: ExecutionIntent) -> OrderResponse:
        """
        Place an order. If LIVE_AUTO_EXECUTION is False, this MUST intercept 
        the intent and route it to the paper/shadow simulation engine.
        """
        pass

    @abc.abstractmethod
    def cancel_order(self, broker_order_id: str) -> OrderResponse:
        """Cancel an open order by broker order ID."""
        pass

    @abc.abstractmethod
    def get_order_status(self, broker_order_id: str) -> OrderResponse:
        """Retrieve current status of a specific order."""
        pass

    @abc.abstractmethod
    def disconnect(slef) -> bool:
        """Terminate broker session safely."""
        pass