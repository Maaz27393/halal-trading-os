import logging
from datetime import datetime
from typing import List, Any
from p4_agents.journal_contracts import JournalReport, ShadowTradeRecord, AttributionSummary
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("TradingJournalAttributionAgent")

class TradingJournalAttributionAgent:
    """
    Decoupled intelligence agent that aggregates completed shadow/paper trades,
    computes performance attributions, and formats structured journal artifacts.
    """

    def __init__(self, permission_gateway: PermissionGateway, brokerage_adapter: Any):
        self.permission_gateway = permission_gateway
        self.brokerage = brokerage_adapter
        logger.info("TradingJournalAttributionAgent initialized.")

    def generate_journal(self, caller_role: str = "analyst_agent") -> JournalReport:
        """
        Orchestrate trade ingestion and attribution analysis:
        1. Verify READ permissions.
        2. Ingest completed shadow trades from simulation/broker adapter.
        3. Compute aggregate metrics (win rate, total PnL, average slippage, realized RR).
        4. Produce structured journal report.
        """
        if not self.permission_gateway.verify_permission(caller_role, "READ"):
            raise PermissionError(f"Caller role '{caller_role}' lacks permission for 'READ'.")

        logger.info("Fetching completed shadow trades for attribution analysis...")
        raw_trades = self.brokerage.get_completed_shadow_trades()

        trade_records: List[ShadowTradeRecord] = []
        total_pnl = 0.0
        wins = 0
        losses = 0
        total_slippage = 0.0
        total_rr = 0.0

        for t in raw_trades:
            pnl = t.get("realized_pnl", 0.0)
            total_pnl += pnl
            if pnl > 0:
                wins += 1
            else:
                losses += 1

            total_slippage += t.get("slippage_pct", 0.0)
            total_rr += t.get("risk_reward_realized", 1.5)

            trade_records.append(
                ShadowTradeRecord(
                    trade_id=t.get("trade_id", "T_001"),
                    symbol=t.get("symbol", "RELIANCE"),
                    entry_price=t.get("entry_price", 2850.0),
                    exit_price=t.get("exit_price", 2920.0),
                    quantity=t.get("quantity", 10),
                    transaction_type=t.get("transaction_type", "BUY"),
                    realized_pnl=pnl,
                    slippage_pct=t.get("slippage_pct", 0.04),
                    risk_reward_realized=t.get("risk_reward_realized", 1.7),
                    compliance_checked=t.get("compliance_checked", True)
                )
            )

        count = len(raw_trades) if raw_trades else 1
        summary = AttributionSummary(
            total_trades=len(raw_trades),
            winning_trades=wins,
            losing_trades=losses,
            win_rate_pct=(wins / len(raw_trades)) * 100 if len(raw_trades) > 0 else 0.0,
            total_realized_pnl=total_pnl,
            average_slippage_pct=total_slippage / count,
            average_rr=total_rr / count
        )

        report = JournalReport(
            timestamp=datetime.utcnow().isoformat(),
            summary=summary,
            trades=trade_records,
            provenance=[
                f"Brokerage Adapter: {self.brokerage.__class__.__name__}",
                f"Governance Guardrail: LIVE_AUTO_EXECUTION = {LIVE_AUTO_EXECUTION}"
            ]
        )

        logger.info("Trading journal attribution report successfully generated.")
        return report