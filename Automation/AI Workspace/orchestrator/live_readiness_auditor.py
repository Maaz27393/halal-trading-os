from typing import Dict, Any, List

class LiveReadinessAuditor:
    """
    Phase 12A: Live Trading Readiness Gate & Account State Reconciler
    Audits live broker session viability, reconciles local vs broker account state,
    and enforces immutable trading risk invariants.
    """
    def __init__(self, broker_session, max_risk_per_trade_pct: float = 1.0, max_trades_per_day: int = 2):
        self.broker = broker_session
        self.max_risk_per_trade_pct = max_risk_per_trade_pct
        self.max_trades_per_day = max_trades_per_day

    def audit_broker_connectivity(self) -> Dict[str, Any]:
        """Validates live API session, token expiry, and broker responsiveness."""
        if not self.broker or not self.broker.is_session_valid():
            return {"ready": False, "reason": "BROKER_SESSION_INVALID_OR_EXPIRED"}
        
        return {"ready": True, "reason": "BROKER_CONNECTED_AND_AUTHENTICATED"}

    def reconcile_account_state(self, local_state: Dict[str, Any], broker_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconciles cash, open positions, and pending orders between local memory and broker API.
        Fails if state drift exceeds tolerance.
        """
        drifts = []

        # 1. Cash Balance Drift
        local_cash = local_state.get("available_cash", 0.0)
        broker_cash = broker_state.get("available_cash", 0.0)
        if abs(local_cash - broker_cash) > 1.0: # 1 Rupee/Unit tolerance
            drifts.append(f"Cash Mismatch: Local={local_cash}, Broker={broker_cash}")

        # 2. Holdings / Positions Count
        local_pos = len(local_state.get("open_positions", []))
        broker_pos = len(broker_state.get("open_positions", []))
        if local_pos != broker_pos:
            drifts.append(f"Open Positions Mismatch: Local={local_pos}, Broker={broker_pos}")

        # 3. Open Orders Count
        local_orders = len(local_state.get("open_orders", []))
        broker_orders = len(broker_state.get("open_orders", []))
        if local_orders != broker_orders:
            drifts.append(f"Open Orders Mismatch: Local={local_orders}, Broker={broker_orders}")

        reconciled = len(drifts) == 0
        return {
            "reconciled": reconciled,
            "drift_count": len(drifts),
            "drifts": drifts,
            "status": "STATE_RECONCILED" if reconciled else "DESYNCHRONIZATION_DETECTED"
        }

    def verify_risk_invariants(self, trade_params: Dict[str, Any], total_equity: float, trades_today_count: int) -> Dict[str, Any]:
        """Enforces non-negotiable risk constraints: risk/trade, trade caps, product type limits."""
        # Check Daily Trade Count Limit
        if trades_today_count >= self.max_trades_per_day:
            return {"passed": False, "reason": f"DAILY_TRADE_LIMIT_EXCEEDED ({trades_today_count}/{self.max_trades_per_day})"}

        # Check Restricted Instruments (No F&O, No Shorting, No Leverage)
        product_type = trade_params.get("product_type", "").upper()
        if product_type in ["FUTURES", "OPTIONS", "MARGIN", "SHORT"]:
            return {"passed": False, "reason": f"UNAUTHORIZED_PRODUCT_TYPE ({product_type})"}

        # Check Per-Trade Capital Risk Limit
        risk_amount = trade_params.get("risk_amount", 0.0)
        max_allowed_risk = total_equity * (self.max_risk_per_trade_pct / 100.0)
        if risk_amount > max_allowed_risk:
            return {"passed": False, "reason": f"EXCEEDS_MAX_RISK_PER_TRADE ({risk_amount} > {max_allowed_risk})"}

        # Check Minimum Risk:Reward Ratio (>= 1.5)
        rr_ratio = trade_params.get("risk_reward_ratio", 0.0)
        if rr_ratio < 1.5:
            return {"passed": False, "reason": f"SUBPAR_RISK_REWARD_RATIO ({rr_ratio} < 1.5)"}

        return {"passed": True, "reason": "ALL_RISK_INVARIANTS_SATISFIED"}
