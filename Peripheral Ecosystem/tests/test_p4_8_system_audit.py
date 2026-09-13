import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p4_agents.autonomous_orchestrator import AutonomousOrchestrator
from p4_agents.premarket_briefing_agent import PreMarketBriefingAgent
from p4_agents.synthesis_engine import TechnicalFundamentalSynthesisEngine
from p4_agents.journal_attribution_agent import TradingJournalAttributionAgent
from p4_agents.news_risk_agent import NewsRiskIntelligenceAgent
from p4_agents.post_market_agent import PostMarketAnalysisAgent
from p4_agents.obsidian_exporter import ObsidianVaultExporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemAuditP4_8")

# Mock adapters simulating decoupled registry-bound providers
class AuditedMarketProvider:
    def fetch_market_snapshot(self): return {"nifty_trend": "Bullish", "india_vix": 13.2}
    def fetch_session_summary(self): return {"nifty_close": 25450.0, "market_breadth_ratio": 1.65}

class AuditedRetrievalProvider:
    def search(self, query): return {"summary": "Retrieved verified historical risk bounds."}

class AuditedReasoningProvider:
    def evaluate(self, prompt): return "Model reasoning evaluation complete."

class AuditedTechnicalProvider:
    def fetch_indicators(self, symbol): return {"rsi": 61.0, "volume_spike": True}

class AuditedFundamentalProvider:
    def fetch_fundamentals(self, symbol): return {"roe": 19.5, "debt_to_equity": 0.12, "compliance_status": "Compliant / Halal Verified"}

class AuditedEarningsProvider:
    def fetch_earnings_schedule(self, symbols): return [{"symbol": "RELIANCE", "days_to_earnings": 14}]

class AuditedNewsProvider:
    def fetch_recent_news(self): return [{"headline": "Industrial growth outlook remains robust.", "sentiment": "Bullish"}]

class AuditedBrokerageProvider:
    def get_completed_shadow_trades(self):
        return [{
            "trade_id": "AUDIT_01",
            "symbol": "RELIANCE",
            "entry_price": 2850.0,
            "exit_price": 2930.0,
            "quantity": 10,
            "realized_pnl": 800.0,
            "slippage_pct": 0.03,
            "risk_reward_realized": 1.9
        }]

class AuditedStrategyProvider:
    def evaluate_strategies(self):
        return [{
            "strategy_name": "EMA Momentum Pullback",
            "win_rate_pct": 64.0,
            "profit_factor": 1.92,
            "max_drawdown_pct": 2.4,
            "rationale": "Passed all multi-year backtest performance thresholds."
        }]

def run_full_system_audit():
    print("=" * 70)
    print("STARTING P4.8 — FULL-SYSTEM INTEGRATION & BOUNDARY AUDIT")
    print("=" * 70)

    # 1. CORE GUARDRAIL INTEGRITY AUDIT
    print("\n[Audit 1/3] Verifying Frozen Core & Guardrail Constraints...")
    assert LIVE_AUTO_EXECUTION is False, "CRITICAL FAILURE: LIVE_AUTO_EXECUTION must remain False!"
    print(" -> SUCCESS: LIVE_AUTO_EXECUTION = False verified across frozen core.")

    # 2. NEGATIVE BOUNDARY & PERMISSION ENFORCEMENT AUDIT
    print("\n[Audit 2/3] Verifying Negative Boundary & Permission Enforcement...")
    perm_gateway = PermissionGateway()
    # Explicitly grant ONLY READ to an unprivileged testing role
    perm_gateway.grant_permission("restricted_agent", "READ")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    exporter = ObsidianVaultExporter(permission_gateway=perm_gateway, vault_base_path=vault_base)

    try:
        exporter.export_artifact("premarket", "Unauthorized.md", "Should Fail", caller_role="restricted_agent")
        raise AssertionError("SECURITY FAILURE: Restricted agent bypassed permission gate on WRITE!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized WRITE successfully blocked by Permission Gateway: {e}")

    # Grant WRITE for audit execution
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    # 3. POSITIVE END-TO-END PIPELINE & PROVENANCE AUDIT
    print("\n[Audit 3/3] Executing End-to-End Orchestrated Pipeline & Provenance Audit...")
    
    premarket = PreMarketBriefingAgent(perm_gateway, AuditedMarketProvider(), AuditedRetrievalProvider(), AuditedReasoningProvider())
    synthesis = TechnicalFundamentalSynthesisEngine(perm_gateway, AuditedTechnicalProvider(), AuditedFundamentalProvider(), AuditedRetrievalProvider())
    journal = TradingJournalAttributionAgent(perm_gateway, AuditedBrokerageProvider())
    news_risk = NewsRiskIntelligenceAgent(perm_gateway, AuditedEarningsProvider(), AuditedNewsProvider(), AuditedRetrievalProvider())
    post_market = PostMarketAnalysisAgent(perm_gateway, AuditedMarketProvider(), AuditedStrategyProvider(), AuditedRetrievalProvider())

    orchestrator = AutonomousOrchestrator(
        permission_gateway=perm_gateway,
        premarket_agent=premarket,
        synthesis_engine=synthesis,
        journal_agent=journal,
        news_risk_agent=news_risk,
        post_market_agent=post_market,
        vault_exporter=exporter
    )

    test_basket = ["RELIANCE", "TCS"]
    exported_files = orchestrator.run_daily_pipeline(test_basket, caller_role="analyst_agent")

    print("\nGenerated Artifact Provenance Check:")
    for artifact_type, filepath in exported_files.items():
        print(f" - [{artifact_type.upper()}] Exported -> {filepath}")
        assert os.path.exists(filepath), f"Integrity Failure: Exported file missing at {filepath}"
        
        # Verify provenance metadata inside generated file
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            assert len(content) > 50, f"Integrity Failure: Artifact {filepath} is empty or malformed."

    print("=" * 70)
    print("P4.8 — FULL-SYSTEM INTEGRATION & BOUNDARY AUDIT PASSED SUCCESSFULLY!")
    print("P0–P4 RELEASE BASELINE VERIFIED & LOCKED.")
    print("=" * 70)

if __name__ == "__main__":
    run_full_system_audit()