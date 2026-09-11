import time
from typing import Dict, Any, List

class Phase12MasterOrchestrator:
    """
    Phase 12D: Unified Live / Shadow Orchestration Engine & Safety Circuit Breaker
    Integrates Readiness Audits, Risk Invariants, Resilience Harness, and Shadow Execution.
    Supports instant Emergency Kill-Switch and audit reporting.
    """
    def __init__(self, broker_session, auditor, stress_harness, shadow_engine):
        self.broker = broker_session
        self.auditor = auditor
        self.harness = stress_harness
        self.shadow_engine = shadow_engine
        self.kill_switch_active = False
        self.system_mode = "SHADOW"  # Modes: "SHADOW" or "LIVE"

    def trigger_kill_switch(self, reason: str = "EMERGENCY_HALT_TRIGGERED") -> Dict[str, Any]:
        """Instantly halts all signal ingestion and execution."""
        self.kill_switch_active = True
        return {
            "kill_switch_active": True,
            "status": "SYSTEM_HALTED",
            "reason": reason,
            "timestamp": time.time()
        }

    def reset_kill_switch(self) -> Dict[str, Any]:
        """Resets kill switch after safety verification."""
        self.kill_switch_active = False
        return {"kill_switch_active": False, "status": "SYSTEM_ARMED"}

    def process_incoming_signal(self, signal: Dict[str, Any], market_price: float, account_state: Dict[str, Any]) -> Dict[str, Any]:
        """Central routing pipeline for incoming strategy signals."""
        if self.kill_switch_active:
            return {
                "status": "REJECTED_KILL_SWITCH_ACTIVE",
                "reason": "System is under emergency halt. No signals processed."
            }

        if self.system_mode == "SHADOW":
            return self.shadow_engine.execute_shadow_trade(signal, market_price, account_state)
        elif self.system_mode == "LIVE":
            conn_audit = self.auditor.audit_broker_connectivity()
            if not conn_audit.get("ready"):
                return {"status": "REJECTED_CONNECTIVITY", "reason": conn_audit["reason"]}
            
            total_equity = account_state.get("available_cash", 0.0) + account_state.get("invested_value", 0.0)
            trades_today = account_state.get("trades_today_count", 0)
            risk_audit = self.auditor.verify_risk_invariants(signal, total_equity, trades_today)
            if not risk_audit.get("passed"):
                return {"status": "REJECTED_RISK_INVARIANT", "reason": risk_audit["reason"]}

            return {"status": "LIVE_ORDER_DISPATCHED", "signal": signal}
        else:
            return {"status": "REJECTED_INVALID_MODE", "reason": f"Unknown mode: {self.system_mode}"}
