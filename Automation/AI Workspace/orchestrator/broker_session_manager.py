import time
from typing import Dict, Any, Optional

class BrokerSessionManager:
    """
    Phase 11A: Broker API Connector & Token Session Manager
    Manages live authentication tokens, TOTP re-authentication cycles,
    session health monitoring, and standardized live order request payloads.
    """
    def __init__(self, broker_name: str = "Shoonya", token_expiry_seconds: int = 86400):
        self.broker_name = broker_name
        self.token_expiry_seconds = token_expiry_seconds
        self.active_session: Optional[Dict[str, Any]] = None

    def authenticate(self, api_key: str, user_id: str, totp_token: str) -> Dict[str, Any]:
        """Simulates authentication handshake and issues a validated session token."""
        if not api_key or not user_id or not totp_token:
            return {"status": "FAILED", "reason": "Missing required credentials"}

        now = int(time.time())
        self.active_session = {
            "broker": self.broker_name,
            "user_id": user_id,
            "access_token": f"TOKEN_{user_id}_{now}",
            "created_at": now,
            "expires_at": now + self.token_expiry_seconds,
            "is_active": True
        }
        return {"status": "SUCCESS", "session": self.active_session}

    def is_session_valid(self) -> bool:
        """Verifies if the current session token exists, is active, and is not expired."""
        if not self.active_session or not self.active_session.get("is_active"):
            return False
        return int(time.time()) < self.active_session.get("expires_at", 0)

    def format_live_order_payload(self, ticker: str, side: str, qty: int, order_type: str = "LIMIT", price: float = 0.0) -> Dict[str, Any]:
        """Translates strategy signals into standardized broker execution payloads."""
        if not self.is_session_valid():
            raise PermissionError("Cannot format live order: Invalid or expired broker session")

        return {
            "broker": self.broker_name,
            "token": self.active_session["access_token"],
            "trading_symbol": ticker,
            "transaction_type": side.upper(),
            "quantity": qty,
            "price_type": order_type.upper(),
            "price": price if order_type.upper() == "LIMIT" else 0.0,
            "product_type": "MIS", # Intraday default
            "exchange": "NSE"
        }
