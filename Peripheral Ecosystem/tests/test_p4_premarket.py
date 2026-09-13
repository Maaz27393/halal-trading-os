import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p4_agents.premarket_briefing_agent import PreMarketBriefingAgent
from connectors.broker_base import LIVE_AUTO_EXECUTION

# Mock abstract capability adapters to adhere to decoupled design
class MockMarketDataCapability:
    def fetch_market_snapshot(self):
        return {
            "nifty_trend": "Bullish Continuation",
            "advance_decline": "1.65",
            "india_vix": 12.8,
            "global_cues": "Strong positive momentum"
        }

class MockKnowledgeRetrievalCapability:
    def search(self, query: str):
        return {"summary": "Retrieved volatility threshold: VIX < 15 permits standard risk allocation."}

class MockReasoningCapability:
    def evaluate(self, prompt: str):
        return "Synthesized analytical output."

def run_premarket_agent_test():
    print("Initializing P4.1 - Pre-Market Regime & Briefing Agent Verification...")

    # 1. Verify frozen core governance guardrail
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Initialize security and capability bindings
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    market_adapter = MockMarketDataCapability()
    retrieval_adapter = MockKnowledgeRetrievalCapability()
    reasoning_adapter = MockReasoningCapability()

    agent = PreMarketBriefingAgent(
        permission_gateway=perm_gateway,
        market_data_capability=market_adapter,
        knowledge_retrieval_capability=retrieval_adapter,
        reasoning_capability=reasoning_adapter
    )

    # 3. Generate Briefing
    briefing = agent.generate_briefing(caller_role="analyst_agent")

    # 4. Validate output structure and contents
    print(f"Generated Briefing Timestamp: {briefing.timestamp}")
    print(f"Market Bias: {briefing.regime.market_bias}")
    print(f"Trading Environment Status: {briefing.environment.environment_status}")
    print(f"Watchlist Candidate Count: {len(briefing.watchlist)}")

    assert briefing.regime.market_bias == "Moderately Bullish"
    assert briefing.environment.environment_status == "Go"
    assert len(briefing.watchlist) == 1
    assert "LIVE_AUTO_EXECUTION = False" in briefing.provenance[2]

    print("P4.1 Pre-Market Regime & Briefing Agent Verified Successfully!")

if __name__ == "__main__":
    run_premarket_agent_test()