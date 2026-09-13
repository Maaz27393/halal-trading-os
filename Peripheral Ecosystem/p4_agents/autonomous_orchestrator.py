import logging
from datetime import datetime
from typing import Dict, Any
from p4_agents.premarket_briefing_agent import PreMarketBriefingAgent
from p4_agents.synthesis_engine import TechnicalFundamentalSynthesisEngine
from p4_agents.journal_attribution_agent import TradingJournalAttributionAgent
from p4_agents.news_risk_agent import NewsRiskIntelligenceAgent
from p4_agents.post_market_agent import PostMarketAnalysisAgent
from p4_agents.obsidian_exporter import ObsidianVaultExporter
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("AutonomousOrchestrator")

class AutonomousOrchestrator:
    """
    Orchestrates the end-to-end P4 Agentic Intelligence pipeline,
    triggering scheduled research workflows and exporting structured artifacts to Obsidian.
    """

    def __init__(
        self,
        permission_gateway: PermissionGateway,
        premarket_agent: PreMarketBriefingAgent,
        synthesis_engine: TechnicalFundamentalSynthesisEngine,
        journal_agent: TradingJournalAttributionAgent,
        news_risk_agent: NewsRiskIntelligenceAgent,
        post_market_agent: PostMarketAnalysisAgent,
        vault_exporter: ObsidianVaultExporter
    ):
        self.permission_gateway = permission_gateway
        self.premarket = premarket_agent
        self.synthesis = synthesis_engine
        self.journal = journal_agent
        self.news_risk = news_risk_agent
        self.post_market = post_market_agent
        self.exporter = vault_exporter
        logger.info("AutonomousOrchestrator initialized with all P4 agent bindings.")

    def run_daily_pipeline(self, watchlist_symbols: list[str], caller_role: str = "analyst_agent") -> Dict[str, str]:
        """
        Execute the full daily research pipeline:
        1. Verify execution guardrail (LIVE_AUTO_EXECUTION == False).
        2. Execute Pre-Market Briefing & export to Obsidian.
        3. Execute Technical + Fundamental Synthesis & export.
        4. Execute News & Earnings Risk Assessment & export.
        5. Execute Trading Journal Attribution & export.
        6. Execute Post-Market Analysis & export.
        """
        # Guardrail check
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is True!")

        logger.info("Starting Autonomous Daily Research Pipeline execution...")
        results = {}
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

        # 1. Pre-Market Briefing
        briefing = self.premarket.generate_briefing(caller_role)
        briefing_md = f"""---
date: {date_str}
type: pre-market-briefing
bias: {briefing.regime.market_bias}
guardrail: LIVE_AUTO_EXECUTION=FALSE
---

# Pre-Market Briefing - {date_str}

## Market Regime
- **Nifty Trend**: {briefing.regime.nifty_trend}
- **Advance / Decline**: {briefing.regime.advance_decline}
- **India VIX**: {briefing.regime.india_vix}
- **Market Bias**: {briefing.regime.market_bias}
- **Confidence**: {briefing.regime.confidence_evidence}

## Trading Environment
- **Status**: {briefing.environment.environment_status}
- **Applicable Conditions**: {', '.join(briefing.environment.applicable_conditions)}
- **Warnings**: {', '.join(briefing.environment.warnings)}
"""
        results["premarket"] = self.exporter.export_artifact("premarket", f"PreMarket_{date_str}.md", briefing_md, caller_role)

        # 2. Technical + Fundamental Synthesis
        synth_report = self.synthesis.run_synthesis(watchlist_symbols, caller_role)
        synth_md = f"""---
date: {date_str}
type: synthesis-report
total_screened: {synth_report.total_screened}
qualified_count: {synth_report.qualified_count}
---

# Technical + Fundamental Synthesis - {date_str}

## Summary
- **Total Screened**: {synth_report.total_screened}
- **Qualified High Conviction**: {synth_report.qualified_count}

## Candidate Evaluations
"""
        for item in synth_report.synthesis_items:
            synth_md += f"""### {item.symbol}
- **Verdict**: {item.verdict}
- **Technical RSI**: {item.technical.rsi} | Volume Spike: {item.technical.volume_spike}
- **Fundamental ROE**: {item.fundamental.roe}% | D/E: {item.fundamental.debt_to_equity} | Compliance: {item.fundamental.compliance_status}
- **Rationale**: {item.synthesis_rationale}
"""
        results["synthesis"] = self.exporter.export_artifact("synthesis", f"Synthesis_{date_str}.md", synth_md, caller_role)

        # 3. News & Earnings Risk Assessment
        risk_report = self.news_risk.assess_risks(watchlist_symbols, caller_role)
        risk_md = f"""---
date: {date_str}
type: news-risk-assessment
---

# News & Earnings Risk Assessment - {date_str}

## Earnings Blackout Risks
"""
        for e in risk_report.earnings_risks:
            risk_md += f"- **{e.symbol}**: Earnings on {e.earnings_date} ({e.days_to_earnings} days) | Risk: {e.risk_level} | Action: {e.actionable_restriction}\n"

        risk_md += "\n## Macro Warnings\n"
        for w in risk_report.macro_warnings:
            risk_md += f"- {w}\n"

        results["news_risk"] = self.exporter.export_artifact("news_risk", f"RiskAssessment_{date_str}.md", risk_md, caller_role)

        # 4. Trading Journal Attribution
        journal_report = self.journal.generate_journal(caller_role)
        journal_md = f"""---
date: {date_str}
type: trading-journal
total_trades: {journal_report.summary.total_trades}
win_rate: {journal_report.summary.win_rate_pct}%
realized_pnl: {journal_report.summary.total_realized_pnl}
---

# Trading Journal & Shadow Attribution - {date_str}

## Performance Summary
- **Total Trades**: {journal_report.summary.total_trades}
- **Win Rate**: {journal_report.summary.win_rate_pct}%
- **Total Realized PnL**: {journal_report.summary.total_realized_pnl}
- **Average Slippage**: {journal_report.summary.average_slippage_pct}%
"""
        results["journal"] = self.exporter.export_artifact("journal", f"Journal_{date_str}.md", journal_md, caller_role)

        # 5. Post-Market Analysis
        post_report = self.post_market.generate_report(caller_role)
        post_md = f"""---
date: {date_str}
type: post-market-analysis
nifty_close: {post_report.session.nifty_close}
---

# Post-Market Analysis - {date_str}

## Session Summary
- **Nifty Close**: {post_report.session.nifty_close}
- **Breadth Ratio**: {post_report.session.market_breadth_ratio}
- **Shadow Turnover**: {post_report.session.total_shadow_turnover}
- **Sector Leader**: {post_report.session.key_sector_leader}

## Strategy Hypothesis Evaluations
"""
        for s in post_report.strategy_evaluations:
            post_md += f"- **{s.strategy_name}**: Win Rate {s.backtest_win_rate_pct}% | PF {s.profit_factor} | Status: **{s.hypothesis_status}**\n"

        results["post_market"] = self.exporter.export_artifact("post_market", f"PostMarket_{date_str}.md", post_md, caller_role)

        logger.info("Autonomous daily research pipeline executed successfully across all modules.")
        return results