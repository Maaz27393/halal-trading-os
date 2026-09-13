import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("B1ScreenerAnalyticsEngine")

class StockMetricItem(BaseModel):
    symbol: str
    sector: str
    roe: float
    rsi: float
    volume_spike_ratio: float
    is_compliant: bool = True
    has_execution_payload: bool = False

class B1ScreenerAnalyticsEngine:
    """
    Track B.1: Advanced Screener & Technical Analytics Engine.
    Processes stock screening datasets, filters compliance criteria (ROE, Volume, RSI),
    and generates structured analytical watchlists.
    Enforces strict permission gating via PermissionGateway.
    Maintains zero execution authority.
    """

    def __init__(self, permission_gateway: PermissionGateway, role: str = "analyst_agent"):
        self.permission_gateway = permission_gateway
        self._connected = False
        self._role = role
        logger.info("B1ScreenerAnalyticsEngine initialized with secure analytics boundary.")

    def connect(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """Establish secure boundary connection for analytics processing."""
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")
        
        if not self.permission_gateway.verify_permission(self._role, "READ"):
            logger.error(f"Analytics connection denied: Role '{self._role}' lacks READ permission.")
            raise PermissionError(f"Role '{self._role}' lacks analytics read permissions.")

        self._connected = True
        logger.info("B1ScreenerAnalyticsEngine successfully connected (Analytics Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        """Return engine health status."""
        return {
            "status": "HEALTHY" if self._connected else "DISCONNECTED",
            "engine": "B1ScreenerAnalyticsEngine",
            "live_auto_execution": LIVE_AUTO_EXECUTION,
            "permissions": "ANALYTICS READ-ONLY"
        }

    def capabilities(self) -> List[str]:
        """Declare strict analytical capabilities."""
        return [
            "filter_screener_universe",
            "calculate_technical_indicators",
            "verify_fundamental_compliance",
            "generate_watchlist_report"
        ]

    def process_universe(self, raw_stocks: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[StockMetricItem]:
        """
        Filter and process raw stock screening data against strict compliance and technical thresholds.
        Enforces strict READ/ANALYTICS permission gating.
        """
        if not self._connected:
            raise ConnectionError("B1ScreenerAnalyticsEngine is not connected.")

        if not self.permission_gateway.verify_permission(self._role, "READ"):
            raise PermissionError(f"Permission DENIED for role '{self._role}' on operation 'READ'.")

        min_roe = criteria.get("min_roe", 12.0)
        max_rsi = criteria.get("max_rsi", 70.0)
        min_volume_spike = criteria.get("min_volume_spike", 1.2)

        logger.info(f"Filtering stock universe with criteria: ROE >= {min_roe}, RSI <= {max_rsi}, Volume Spike >= {min_volume_spike}")

        processed_items = []
        for stock in raw_stocks:
            roe = stock.get("roe", 0.0)
            rsi = stock.get("rsi", 50.0)
            vol_spike = stock.get("volume_spike_ratio", 1.0)
            compliant = stock.get("is_compliant", True)

            if roe >= min_roe and rsi <= max_rsi and vol_spike >= min_volume_spike and compliant:
                processed_items.append(
                    StockMetricItem(
                        symbol=stock.get("symbol", "UNKNOWN"),
                        sector=stock.get("sector", "General"),
                        roe=roe,
                        rsi=rsi,
                        volume_spike_ratio=vol_spike,
                        is_compliant=compliant,
                        has_execution_payload=False
                    )
                )

        logger.info(f"Filtered {len(processed_items)} compliant stocks out of {len(raw_stocks)} total entries.")
        return processed_items

    def disconnect(self) -> bool:
        """Disconnect and clear session boundary."""
        self._connected = False
        logger.info("B1ScreenerAnalyticsEngine disconnected.")
        return True