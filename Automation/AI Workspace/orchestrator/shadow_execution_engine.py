import time
from typing import Dict, Any, List

class ShadowExecutionEngine:
    """
    Phase 12C: Shadow Execution Engine & Real-Time Telemetry Monitor
    Executes paper/shadow trades on live market signals without sending orders to broker.
    Logs audit trails, risk checks, latency telemetry, and simulated fills.
    """
    def __init__(self, readiness_auditor, stress_harness):
        self.auditor = readiness_auditor
        self.harness = stress_harness
        self.telemetry_logs: List[Dict[str, Any]] = []

    def execute_shadow_trade(self, signal: Dict[str, Any], market_price: float, account_state: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.perf_counter()

        # 1. Connectivity Audit
        conn_audit = self.auditor.audit_broker_connectivity()
        if not conn_audit.get("ready"):
            return self._log_telemetry(signal, "REJECTED_CONNECTIVITY", conn_audit["reason"], start_time)

        # 2. Risk Invariants Gate
        total_equity = account_state.get("available_cash", 0.0) + account_state.get("invested_value", 0.0)
        trades_today = account_state.get("trades_today_count", 0)
        risk_audit = self.auditor.verify_risk_invariants(signal, total_equity, trades_today)
        if not risk_audit.get("passed"):
            return self._log_telemetry(signal, "REJECTED_RISK_INVARIANT", risk_audit["reason"], start_time)

        # 3. Pre-Trade Post-Signal Slippage Check
        expected_price = signal.get("trigger_price", market_price)
        slippage_audit = self.harness.check_post_signal_slippage(expected_price, market_price)
        if not slippage_audit.get("allowed"):
            return self._log_telemetry(signal, "ABORTED_SLIPPAGE_SURGE", slippage_audit["reason"], start_time)

        # 4. Simulated Shadow Fill Execution
        shadow_order_id = f"SHADOW_{int(time.time() * 1000)}"
        fill_summary = {
            "shadow_order_id": shadow_order_id,
            "symbol": signal.get("trading_symbol"),
            "action": signal.get("action", "BUY"),
            "qty": signal.get("quantity"),
            "expected_price": expected_price,
            "fill_price": market_price,
            "slippage_pct": slippage_audit.get("drift_pct", 0.0),
            "status": "SIMULATED_FILL_EXECUTED"
        }

        return self._log_telemetry(signal, "FILLED_SHADOW", "SHADOW_ORDER_EXECUTED_SUCCESSFULLY", start_time, fill_summary)

    def _log_telemetry(self, signal: Dict[str, Any], status: str, reason: str, start_time: float, fill_details: Dict[str, Any] = None) -> Dict[str, Any]:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 3)
        log_entry = {
            "symbol": signal.get("trading_symbol", "UNKNOWN"),
            "status": status,
            "reason": reason,
            "latency_ms": latency_ms,
            "fill": fill_details or {}
        }
        self.telemetry_logs.append(log_entry)
        return log_entry

    def get_telemetry_summary(self) -> Dict[str, Any]:
        total = len(self.telemetry_logs)
        filled = sum(1 for log in self.telemetry_logs if log["status"] == "FILLED_SHADOW")
        rejected = total - filled
        avg_latency = round(sum(log["latency_ms"] for log in self.telemetry_logs) / total, 3) if total > 0 else 0.0

        return {
            "total_signals_processed": total,
            "shadow_orders_filled": filled,
            "orders_rejected_or_aborted": rejected,
            "avg_latency_ms": avg_latency
        }
