import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p4_agents.news_risk_agent import NewsRiskIntelligenceAgent
from connectors.broker_base import LIVE_AUTO_EXECUTION

class MockEarningsProvider:
    def fetch_earnings_schedule(self, symbols):
        return [
            {"symbol": "RELIANCE", "earnings_date": "2026-09-15", "days_to_earnings": 2},
            {"symbol": "TCS", "earnings_date": "2026-09-28", "days_to_earnings": 15}
        ]

class MockNewsProvider:
    def fetch_recent_news(self):
        return [
            {
                "headline": "RBI maintains steady repo rate outlook.",
                "source": "Economic Times",
                "sentiment": "Bullish",
                "impact_score": 0.8,
                "relevant_symbols": ["RELIANCE", "TCS", "INFY"]
            }
        ]

class MockKnowledgeRetrieval:
    def search(self, query: str):
        return {"summary": "Earnings within 3 days trigger mandatory position blackouts."}

def run_news_risk_agent_test():
    print("Initializing P4.4 - Earnings-Risk & News Intelligence Agent Verification...")

    # 1. Verify frozen core governance guardrail
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Initialize security and capability bindings
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    earnings_adapter = MockEarningsProvider()
    news_adapter = MockNewsProvider()
    retrieval_adapter = MockKnowledgeRetrieval()

    agent = NewsRiskIntelligenceAgent(
        permission_gateway=perm_gateway,
        earnings_capability=earnings_adapter,
        news_capability=news_adapter,
        knowledge_retrieval_capability=retrieval_adapter
    )

    # 3. Run Risk Assessment
    report = agent.assess_risks(["RELIANCE", "TCS"], caller_role="analyst_agent")

    # 4. Validate output structure and assertions
    print(f"Earnings Risks Evaluated: {len(report.earnings_risks)}")
    print(f"News Headlines Processed: {len(report.news_intelligence)}")
    print(f"RELIANCE Risk Level: {report.earnings_risks[0].risk_level} ({report.earnings_risks[0].actionable_restriction})")
    print(f"TCS Risk Level: {report.earnings_risks[1].risk_level} ({report.earnings_risks[1].actionable_restriction})")

    assert len(report.earnings_risks) == 2
    assert report.earnings_risks[0].risk_level == "High"
    assert report.earnings_risks[1].risk_level == "Low"
    assert len(report.news_intelligence) == 1
    assert "LIVE_AUTO_EXECUTION = False" in report.provenance[3]

    print("P4.4 Earnings-Risk & News Intelligence Agent Verified Successfully!")

if __name__ == "__main__":
    run_news_risk_agent_test()