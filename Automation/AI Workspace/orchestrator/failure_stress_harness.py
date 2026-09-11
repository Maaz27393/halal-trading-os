from typing import Dict, Any

class FailureStressHarness:
    """
    Phase 12B: Failure Injection & Resilience Stress Harness
    Simulates live execution failure states to test system safety guards:
    - Network Timeouts & Connection Drops
    - Mid-Execution Token Expiry
    - Post-Signal Price Drift & Slippage Surges
    - Broker Rejection Error Handling & State Recovery
    """
    def __init__(self, max_allowed_slippage_pct: float = 0.5):
        self.max_allowed_slippage_pct = max_allowed_slippage_pct

    def process_order_with_timeout_guard(self, order_payload: Dict[str, Any], simulate_timeout: bool = False) -> Dict[str, Any]:
        """Simulates API network latency or timeout during live submission."""
        if simulate_timeout:
            return {
                "success": False,
                "status": "TIMEOUT_INTERCEPTED",
                "action": "CANCEL_AND_RECONCILE",
                "reason": "BROKER_API_NETWORK_TIMEOUT"
            }
        return {"success": True, "status": "SUBMITTED"}

    def validate_session_before_dispatch(self, broker_session, simulate_token_expiry: bool = False) -> Dict[str, Any]:
        """Simulates token invalidation immediately prior to order dispatch."""
        if simulate_token_expiry and broker_session:
            broker_session.is_session_valid = lambda: False
            
        if not broker_session or not broker_session.is_session_valid():
            return {
                "dispatch_allowed": False,
                "reason": "TOKEN_EXPIRED_MID_EXECUTION",
                "action": "TRIGGER_AUTO_REAUTH_OR_HALT"
            }
        return {"dispatch_allowed": True, "reason": "SESSION_ACTIVE"}

    def check_post_signal_slippage(self, expected_price: float, current_market_price: float) -> Dict[str, Any]:
        """Intercepts orders if price moves beyond allowable threshold before execution."""
        if expected_price <= 0:
            return {"allowed": False, "reason": "INVALID_EXPECTED_PRICE"}

        drift_pct = (abs(current_market_price - expected_price) / expected_price) * 100.0
        if drift_pct > self.max_allowed_slippage_pct:
            return {
                "allowed": False,
                "drift_pct": round(drift_pct, 4),
                "reason": f"SLIPPAGE_SURGE_EXCEEDED ({drift_pct:.2f}% > {self.max_allowed_slippage_pct}%)",
                "action": "ABORT_ORDER_SUBMISSION"
            }
        return {"allowed": True, "drift_pct": round(drift_pct, 4), "reason": "SLIPPAGE_WITHIN_TOLERANCE"}

    def handle_broker_rejection(self, order_id: str, broker_error_code: str) -> Dict[str, Any]:
        """Processes incoming broker error responses and updates local state machine cleanly."""
        known_errors = {
            "INSUFFICIENT_MARGIN": "HALT_STRATEGY_CHECK_CAPITAL",
            "CIRCUIT_LIMIT_REACHED": "CANCEL_ORDER_MARK_UNSERVICEABLE",
            "EXCHANGE_OFFLINE": "TRIGGER_KILL_SWITCH",
            "INVALID_PRICE_TICK": "RECALIBRATE_TICK_SIZE"
        }
        
        action = known_errors.get(broker_error_code, "UNHANDLED_BROKER_ERROR_HALT")
        return {
            "order_id": order_id,
            "status": "REJECTED_BY_BROKER",
            "broker_error": broker_error_code,
            "system_action": action
        }
