from typing import Dict, Any

class ExecutionSafetyInterlock:
    """
    Phase 11B: Live Execution Safety Interlock & Pre-Trade Risk Guards
    Acts as the final safety firewall before live broker order dispatch.
    Enforces:
    - Emergency Kill-Switch Status
    - Shariah Compliance Validation
    - Max Single Order Value & Fat-Finger Sanity Checks
    - Daily Loss Limit / Max Drawdown Halt
    """
    def __init__(self, max_trade_value: float = 50000.0, max_daily_loss: float = 10000.0, max_price_deviation_pct: float = 3.0):
        self.max_trade_value = max_trade_value
        self.max_daily_loss = max_daily_loss
        self.max_price_deviation_pct = max_price_deviation_pct
        self.kill_switch_active = False

    def trigger_kill_switch(self, active: bool = True):
        self.kill_switch_active = active

    def validate_order(self, order_payload: Dict[str, Any], ltp: float, is_halal: bool, current_daily_loss: float = 0.0) -> Dict[str, Any]:
        if self.kill_switch_active:
            return {"approved": False, "reason": "KILL_SWITCH_ACTIVE"}

        if not is_halal:
            return {"approved": False, "reason": "NON_HALAL_ASSET_REJECTED"}

        qty = order_payload.get("quantity", 0)
        price = order_payload.get("price", ltp)
        if price <= 0:
            price = ltp
            
        trade_value = qty * price

        if trade_value > self.max_trade_value:
            return {"approved": False, "reason": f"EXCEEDS_MAX_TRADE_VALUE ({trade_value:.2f} > {self.max_trade_value:.2f})"}

        if current_daily_loss >= self.max_daily_loss:
            return {"approved": False, "reason": f"DAILY_LOSS_LIMIT_BREACHED ({current_daily_loss:.2f} >= {self.max_daily_loss:.2f})"}

        if ltp > 0 and price > 0:
            deviation = abs(price - ltp) / ltp * 100.0
            if deviation > self.max_price_deviation_pct:
                return {"approved": False, "reason": f"FAT_FINGER_PRICE_DEVIATION ({deviation:.2f}% > {self.max_price_deviation_pct}%)"}

        return {"approved": True, "reason": "PASSED_ALL_RISK_GUARDS"}
