import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p4_agents.post_market_agent import PostMarketAnalysisAgent
from connectors.broker_base import LIVE_AUTO_EXECUTION

class MockMarketDataCapability:
    def fetch_session_summary(self):
        return {
            "date": "2026-09-12",
            "nifty_close": 25420.5,
            "market_breadth_ratio": 1.62,
            "total_shadow_turnover": 520000.0,
            "key_sector_leader": "Banking & Auto"
        }

class MockStrategyCapability:
    def evaluate_strategies(self):
        return [
            {
                "strategy_name": "EMA 20/50 Pullback",
                "win_rate_pct": 62.0,
                "profit_factor": 1.85,
                "max_drawdown_pct": 2.8,
                "rationale": "Maintains robust expectancy under bullish breadth regimes."
            }
        ]

class MockKnowledgeRetrieval:
    def search(self, query: str):
        return {"summary": "Post-market breadth expansion confirms continuation setup validity."}

def run_post_market_agent_test():
    print("Initializing P4.5 - Post-Market Analysis & Strategy Research Assistant Verification...")

    # 1. Verify frozen core governance guardrail
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Initialize security and capability bindings
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    market_adapter = MockMarketDataCapability()
    strategy_adapter = MockStrategyCapability()
    retrieval_adapter = MockKnowledgeRetrieval()

    agent = PostMarketAnalysisAgent(
        permission_gateway=perm_gateway,
        market_data_capability=market_adapter,
        strategy_capability=strategy_adapter,
        knowledge_retrieval_capability=retrieval_adapter
    )

    # 3. Generate Report
    report = agent.generate_report(caller_role="analyst_agent")

    # 4. Validate output structure and assertions
    print(f"Session Date: {report.session.date} | Nifty Close: {report.session.nifty_close}")
    print(f"Strategies Evaluated: {len(report.strategy_evaluations)}")
    print(f"Strategy Status: {report.strategy_evaluations[0].strategy_name} -> {report.strategy_evaluations[0].hypothesis_status}")

    assert report.session.nifty_close == 25420.5
    assert len(report.strategy_evaluations) == 1
    assert report.strategy_evaluations[0].hypothesis_status == "Approved for Paper Forward Testing"
    assert "LIVE_AUTO_EXECUTION = False" in report.provenance[3]

    print("P4.5 Post-Market Analysis & Strategy Research Assistant Verified Successfully!")

if __name__ == "__main__":
    run_post_market_agent_test()