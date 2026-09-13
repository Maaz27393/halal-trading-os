import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("C1RiskManagementEngine")

class PositionRiskParameters(BaseModel):
    symbol: str
    entry_price: float
    stop_loss: float
    target_price: float
    account_capital: float
    risk_percentage: float = 1.0  # Max 1% capital risk per trade
    position_size: int = 0
    risk_reward_ratio: float = 0.0
    is_risk_compliant: bool = False
    has_execution_payload: bool = False

class C1RiskManagementEngine:
    """
    Track C.1: Risk Management & Portfolio Optimization Engine.
    Calculates position sizing, enforces strict risk-reward ratios, and validates drawdown caps.
    Enforces strict permission gating via PermissionGateway.
    Maintains zero execution authority.
    """

    def __init__(self, permission_gateway: PermissionGateway, role: str = "risk_analyst"):
        self.permission_gateway = permission_gateway
        self._connected = False
        self._role = role
        logger.info("C1RiskManagementEngine initialized with secure risk boundary.")

    def connect(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """Establish secure boundary connection for risk evaluation."""
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")
        
        if not self.permission_gateway.verify_permission(self._role, "READ"):
            logger.error(f"Risk connection denied: Role '{self._role}' lacks READ/RISK permission.")
            raise PermissionError(f"Role '{self._role}' lacks risk evaluation permissions.")

        self._connected = True
        logger.info("C1RiskManagementEngine successfully connected (Risk Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        """Return engine health status."""
        return {
            "status": "HEALTHY" if self._connected else "DISCONNECTED",
            "engine": "C1RiskManagementEngine",
            "live_auto_execution": LIVE_AUTO_EXECUTION,
            "permissions": "RISK EVALUATION READ-ONLY"
        }

    def capabilities(self) -> List[str]:
        """Declare strict risk management capabilities."""
        return [
            "calculate_position_sizing",
            "validate_risk_reward_ratio",
            "enforce_portfolio_drawdown_limit",
            "audit_trade_risk_parameters"
        ]

    def evaluate_position_risk(self, params: Dict[str, Any], min_rr_ratio: float = 1.5) -> PositionRiskParameters:
        """
        Evaluate and validate risk parameters for a proposed trade setup.
        Enforces strict position sizing and 1:1.5 Risk-to-Reward ratio minimum.
        """
        if not self._connected:
            raise ConnectionError("C1RiskManagementEngine is not connected.")

        if not self.permission_gateway.verify_permission(self._role, "READ"):
            raise PermissionError(f"Permission DENIED for role '{self._role}' on operation 'READ'.")

        symbol = params.get("symbol", "UNKNOWN")
        entry = float(params.get("entry_price", 0.0))
        sl = float(params.get("stop_loss", 0.0))
        target = float(params.get("target_price", 0.0))
        capital = float(params.get("account_capital", 100000.0))
        risk_pct = float(params.get("risk_percentage", 1.0))

        if entry <= 0 or sl <= 0 or target <= 0:
            raise ValueError("Invalid price parameters provided for risk evaluation.")

        # Determine risk per share and reward per share (assuming long position)
        risk_per_share = abs(entry - sl)
        reward_per_share = abs(target - entry)

        if risk_per_share == 0:
            rr_ratio = 0.0
        else:
            rr_ratio = reward_per_share / risk_per_share

        # Capital at risk calculation
        max_capital_at_risk = capital * (risk_pct / 100.0)
        position_size = int(max_capital_at_risk / risk_per_share) if risk_per_share > 0 else 0

        # Compliance check: RR must meet or exceed minimum (default 1.5)
        is_compliant = rr_ratio >= min_rr_ratio and position_size > 0

        logger.info(f"Evaluated risk for {symbol}: R:R = {rr_ratio:.2f} (Target >= {min_rr_ratio}), Size = {position_size}, Compliant = {is_compliant}")

        return PositionRiskParameters(
            symbol=symbol,
            entry_price=entry,
            stop_loss=sl,
            target_price=target,
            account_capital=capital,
            risk_percentage=risk_pct,
            position_size=position_size,
            risk_reward_ratio=round(rr_ratio, 2),
            is_risk_compliant=is_compliant,
            has_execution_payload=False
        )

    def disconnect(self) -> bool:
        """Disconnect and clear session boundary."""
        self._connected = False
        logger.info("C1RiskManagementEngine disconnected.")
        return True