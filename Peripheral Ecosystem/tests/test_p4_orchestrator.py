import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p4_agents.autonomous_orchestrator import AutonomousOrchestrator
from p4_agents.premarket_briefing_agent import PreMarketBriefingAgent
from p4_agents.synthesis_engine import TechnicalFundamentalSynthesisEngine
from p4_agents.journal_attribution_agent import TradingJournalAttributionAgent
from p4_agents.news_risk_agent import NewsRiskIntelligenceAgent
from p4_agents.post_market_agent import PostMarketAnalysisAgent
from p4_agents.obsidian_exporter import ObsidianVaultExporter
from connectors.broker_base import LIVE_AUTO_EXECUTION

# Mock dependencies for end-to-end integration test
class MockMarket:
    def fetch_market_snapshot(self): return {"nifty_trend": "Bullish"}
    def fetch_session_summary(self): return {"nifty_close": 25420.0, "market_breadth_ratio": 1.6}

class MockRetrieval:
    def search(self, query): return {"summary": "Standard risk rules applied."}

class MockReasoning:
    def evaluate(self, prompt): return "Evaluated."

class MockTech:
    def fetch_indicators(self, sym): return {"rsi": 60.0, "volume_spike": True}

class MockFund:
    def fetch_fundamentals(self, sym): return {"roe": 20.0, "debt_to_equity": 0.1, "compliance_status": "Compliant"}

class MockEarnings:
    def fetch_earnings_schedule(self, syms): return [{"symbol": "RELIANCE", "days_to_earnings": 10}]

class MockNews:
    def fetch_recent_news(self): return [{"headline": "Market stable", "sentiment": "Bullish"}]

class MockBroker:
    def get_completed_shadow_trades(self): return [{"trade_id": "T1", "symbol": "RELIANCE", "realized_pnl": 500.0, "slippage_pct": 0.02}]

class MockStrategy:
    def evaluate_strategies(self): return [{"strategy_name": "EMA Pullback", "profit_factor": 1.7, "max_drawdown_pct": 3.0, "win_rate_pct": 60.0}]

def run_orchestrator_test():
    print("Initializing P4.7 - Autonomous Orchestration & Scheduled Research Dispatcher Verification...")

    # 1. Verify frozen core governance guardrail
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and agents
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    exporter = ObsidianVaultExporter(perm_gateway, vault_base)

    premarket = PreMarketBriefingAgent(perm_gateway, MockMarket(), MockRetrieval(), MockReasoning())
    synthesis = TechnicalFundamentalSynthesisEngine(perm_gateway, MockTech(), MockFund(), MockRetrieval())
    journal = TradingJournalAttributionAgent(perm_gateway, MockBroker())
    news_risk = NewsRiskIntelligenceAgent(perm_gateway, MockEarnings(), MockNews(), MockRetrieval())
    post_market = PostMarketAnalysisAgent(perm_gateway, MockMarket(), MockStrategy(), MockRetrieval())

    orchestrator = AutonomousOrchestrator(
        permission_gateway=perm_gateway,
        premarket_agent=premarket,
        synthesis_engine=synthesis,
        journal_agent=journal,
        news_risk_agent=news_risk,
        post_market_agent=post_market,
        vault_exporter=exporter
    )

    # 3. Run Pipeline
    exported_artifacts = orchestrator.run_daily_pipeline(["RELIANCE", "TCS"], caller_role="analyst_agent")

    # 4. Validate output
    print(f"Pipeline Executed Successfully. Exported Artifacts Count: {len(exported_artifacts)}")
    for key, path in exported_artifacts.items():
        print(f" - {key}: {path}")
        assert os.path.exists(path), f"File missing: {path}"

    print("P4.7 Autonomous Orchestration & Scheduled Research Dispatcher Verified Successfully!")

if __name__ == "__main__":
    run_orchestrator_test()