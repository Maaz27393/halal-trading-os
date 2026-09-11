from typing import Dict, Any, List, Optional
import time

from execution_state_machine import ExecutionOrder, OrderState
from position_state_engine import PositionStateEngine
from pre_execution_revalidation import PreExecutionRevalidator
from order_simulation_engine import OrderSimulationEngine
from execution_reconciliation import ExecutionReconciler
from failure_recovery_engine import FailureRecoveryEngine

class PaperTradingHarness:
    """
    Phase 9G: End-to-End Paper Trading Harness
    Integrates Phases 9A-9F into a unified paper execution engine:
    Signal intake -> Order creation -> Pre-check -> Pre-execution revalidation ->
    Simulation fill -> Reconciliation & Position Sync -> Portfolio MTM.
    """
    def __init__(self, initial_capital: float = 200000.0, max_slippage_pct: float = 0.5):
        self.position_engine = PositionStateEngine(initial_capital=initial_capital)
        self.revalidator = PreExecutionRevalidator(max_stale_seconds=5.0, max_price_drift_pct=0.8)
        self.sim_engine = OrderSimulationEngine(default_slippage_pct=0.05)
        self.reconciler = ExecutionReconciler()
        self.recovery_engine = FailureRecoveryEngine(stale_timeout_seconds=10.0)
        self.max_slippage_pct = max_slippage_pct
        self.order_history: List[ExecutionOrder] = []

    def process_trade_signal(self, signal: Dict[str, Any], live_candle: Dict[str, Any]) -> Dict[str, Any]:
        order_id = f"ORD_{int(time.time()*1000)}"
        ticker = signal.get("ticker", "")
        side = signal.get("side", "BUY")
        qty = int(signal.get("qty", 0))
        limit_price = float(signal.get("limit_price", 0.0))

        # 1. State Machine Initialization (Phase 9A)
        order = ExecutionOrder(
            order_id=order_id,
            ticker=ticker,
            side=side,
            qty=qty,
            limit_price=limit_price,
            max_slippage_pct=self.max_slippage_pct
        )
        self.order_history.append(order)

        # 2. State Machine Precheck Pass
        if not order.pass_precheck():
            return {"status": "REJECTED", "reason": "State machine precheck failed", "order": order.to_dict()}

        # 3. Pre-Execution Revalidation (Phase 9C)
        reval_res = self.revalidator.revalidate(
            order_payload=order.to_dict(),
            live_candle=live_candle,
            available_capital=self.position_engine.available_capital
        )
        if not reval_res["revalidated"]:
            order.reject(reval_res["reason"])
            return {"status": "REJECTED", "reason": reval_res["reason"], "order": order.to_dict()}

        # 4. Submit to Simulated Broker
        order.submit_to_broker(broker_id="PAPER_BROKER_01")

        # 5. Order Execution Simulation (Phase 9D)
        sim_res = self.sim_engine.simulate_fill(order, live_candle)

        # 6. Execution Reconciliation & Position Auto-Sync (Phase 9E & 9B)
        audit_res = self.reconciler.reconcile(order, self.position_engine)

        return {
            "status": sim_res["status"],
            "order": order.to_dict(),
            "revalidation": reval_res,
            "simulation": sim_res,
            "audit": audit_res
        }

    def update_portfolio(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        for ticker, price in current_prices.items():
            self.position_engine.update_market_price(ticker, price)
        return self.position_engine.get_portfolio_summary()
