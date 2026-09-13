import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p4_agents.synthesis_engine import TechnicalFundamentalSynthesisEngine
from connectors.broker_base import LIVE_AUTO_EXECUTION

# Mock abstract capability providers
class MockTechnicalProvider:
    def fetch_indicators(self, symbol: str):
        return {
            "rsi": 62.5,
            "ema_alignment": "Bullish (20 > 50)",
            "volume_spike": True,
            "support_distance_pct": 0.8
        }

class MockFundamentalProvider:
    def fetch_fundamentals(self, symbol: str):
        return {
            "roe": 21.0,
            "debt_to_equity": 0.08,
            "compliance_status": "Compliant / Halal Verified",
            "quarterly_growth_pct": 16.5
        }

class MockKnowledgeRetrieval:
    def search(self, query: str):
        return {"summary": "Momentum continuation patterns supported under current market breadth."}

def run_synthesis_engine_test():
    print("Initializing P4.2 - Technical + Fundamental Synthesis Engine Verification...")

    # 1. Verify frozen core governance guardrail
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Initialize security and capability bindings
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    tech_adapter = MockTechnicalProvider()
    fund_adapter = MockFundamentalProvider()
    retrieval_adapter = MockKnowledgeRetrieval()

    engine = TechnicalFundamentalSynthesisEngine(
        permission_gateway=perm_gateway,
        technical_capability=tech_adapter,
        fundamental_capability=fund_adapter,
        knowledge_retrieval_capability=retrieval_adapter
    )

    # 3. Run Synthesis for test basket
    test_symbols = ["RELIANCE", "TCS", "INFY"]
    report = engine.run_synthesis(test_symbols, caller_role="analyst_agent")

    # 4. Validate output structure and results
    print(f"Total Screened: {report.total_screened}")
    print(f"Qualified High Conviction Count: {report.qualified_count}")
    for item in report.synthesis_items:
        print(f" - Symbol: {item.symbol} | Verdict: {item.verdict}")

    assert report.total_screened == 3
    assert report.qualified_count == 3
    assert report.synthesis_items[0].verdict == "High Conviction"
    assert "LIVE_AUTO_EXECUTION = False" in report.provenance[3]

    print("P4.2 Technical + Fundamental Synthesis Engine Verified Successfully!")

if __name__ == "__main__":
    run_synthesis_engine_test()