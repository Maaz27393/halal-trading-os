import logging
from typing import Any, Dict, Optional
from contracts import ExecutionIntent, OrderResponse
from security.order_validator import OrderValidator, OrderValidationError
from security.gateway import PermissionGateway
from security.kill_switch import EmergencyKillSwitch, KillSwitchTriggeredError
from connectors.broker_base import BaseBrokerConnector, LIVE_AUTO_EXECUTION

logger = logging.getLogger("ExecutionPolicyGateway")

class ExecutionPolicyGateway:
    """
    Centralized execution gateway coordinating pre-trade validation, 
    permission boundaries, emergency kill-switches, and secure broker dispatch.
    """

    def __init__(
        self, 
        broker: BaseBrokerConnector, 
        validator: OrderValidator, 
        permission_gateway: PermissionGateway,
        kill_switch: Optional[EmergencyKillSwitch] = None
    ):
        self.broker = broker
        self.validator = validator
        self.permission_gateway = permission_gateway
        self.kill_switch = kill_switch or EmergencyKillSwitch()
        logger.info("ExecutionPolicyGateway initialized with full policy and kill-switch enforcement.")

    def execute(self, intent: ExecutionIntent, current_market_price: float, caller_role: str = "strategy_engine") -> OrderResponse:
        """
        Orchestrate the end-to-end execution pipeline:
        1. Check Emergency Kill-Switch status.
        2. Verify execution capability permissions.
        3. Validate pre-trade rules (capital, lot size, risk, idempotency).
        4. Check system safety guardrails (LIVE_AUTO_EXECUTION).
        5. Dispatch to broker (Simulated or Shadow mode).
        """
        logger.info(f"Received execution request from '{caller_role}' for symbol {intent.symbol}.")

        # 1. Emergency Kill-Switch Check
        self.kill_switch.check_state()

        # 2. Permission Check
        if not self.permission_gateway.verify_permission(caller_role, "EXECUTE"):
            raise PermissionError(f"Caller role '{caller_role}' lacks permission for 'EXECUTE'.")

        # 3. Pre-trade Validation
        self.validator.validate_intent(intent, current_market_price)

        # 4. Guardrail Enforcement Check
        if not LIVE_AUTO_EXECUTION:
            logger.info("System operating in Paper/Shadow Dispatch mode (LIVE_AUTO_EXECUTION=False).")

        # 5. Broker Dispatch
        response = self.broker.place_order(intent)
        logger.info(f"Execution successfully completed. Broker Order ID: {response.broker_order_id}")
        return response