import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p4_agents.journal_attribution_agent import TradingJournalAttributionAgent
from connectors.broker_base import LIVE_AUTO_EXECUTION

class MockBrokerageAdapter:
    def get_completed_shadow_trades(self):
        return [
            {
                "trade_id": "SHADOW_001",
                "symbol": "RELIANCE",
                "entry_price": 2850.0,
                "exit_price": 2920.0,
                "quantity": 10,
                "transaction_type": "BUY",
                "realized_pnl": 700.0,
                "slippage_pct": 0.03,
                "risk_reward_realized": 1.8
            },
            {
                "trade_id": "SHADOW_002",
                "symbol": "TCS",
                "entry_price": 3400.0,
                "exit_price": 3380.0,
                "quantity": 5,
                "transaction_type": "BUY",
                "realized_pnl": -100.0,
                "slippage_pct": 0.05,
                "risk_reward_realized": 0.5
            }
        ]

def run_journal_agent_test():
    print("Initializing P4.3 - Trading Journal & Shadow Attribution Agent Verification...")

    # 1. Verify frozen core governance guardrail
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Initialize security and capability bindings
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    brokerage_adapter = MockBrokerageAdapter()
    agent = TradingJournalAttributionAgent(
        permission_gateway=perm_gateway,
        brokerage_adapter=brokerage_adapter
    )

    # 3. Generate Journal Report
    report = agent.generate_journal(caller_role="analyst_agent")

    # 4. Validate output structure and metrics
    print(f"Total Trades Logged: {report.summary.total_trades}")
    print(f"Win Rate: {report.summary.win_rate_pct}%")
    print(f"Total Realized PnL: {report.summary.total_realized_pnl}")
    print(f"Average Slippage: {report.summary.average_slippage_pct}%")

    assert report.summary.total_trades == 2
    assert report.summary.winning_trades == 1
    assert report.summary.losing_trades == 1
    assert report.summary.total_realized_pnl == 600.0
    assert "LIVE_AUTO_EXECUTION = False" in report.provenance[1]

    print("P4.3 Trading Journal & Shadow Attribution Agent Verified Successfully!")

if __name__ == "__main__":
    run_journal_agent_test()