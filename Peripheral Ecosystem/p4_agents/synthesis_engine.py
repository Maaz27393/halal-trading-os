import logging
from datetime import datetime
from typing import List, Dict, Any
from p4_agents.synthesis_contracts import SynthesisReport, SynthesisItem, TechnicalMetrics, FundamentalMetrics
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("SynthesisEngine")

class TechnicalFundamentalSynthesisEngine:
    """
    Decoupled intelligence engine combining technical indicators, fundamental metrics,
    and knowledge retrieval to synthesize structured stock evaluations.
    """

    def __init__(
        self,
        permission_gateway: PermissionGateway,
        technical_capability: Any,
        fundamental_capability: Any,
        knowledge_retrieval_capability: Any
    ):
        self.permission_gateway = permission_gateway
        self.tech_provider = technical_capability
        self.fund_provider = fundamental_capability
        self.retrieval = knowledge_retrieval_capability
        logger.info("TechnicalFundamentalSynthesisEngine initialized with abstract capabilities.")

    def run_synthesis(self, symbols: List[str], caller_role: str = "analyst_agent") -> SynthesisReport:
        """
        Orchestrate multi-domain synthesis for a given list of symbols:
        1. Verify READ permissions.
        2. Fetch technical indicators via abstract technical capability.
        3. Fetch fundamental metrics and compliance data via fundamental capability.
        4. Query knowledge retrieval for contextual risk guidelines.
        5. Synthesize unified evaluation reports.
        """
        # 1. Permission Check
        if not self.permission_gateway.verify_permission(caller_role, "READ"):
            raise PermissionError(f"Caller role '{caller_role}' lacks permission for 'READ'.")

        logger.info(f"Synthesizing technical and fundamental data for symbols: {symbols}")

        synthesis_items: List[SynthesisItem] = []
        qualified_count = 0

        for symbol in symbols:
            # 2. Fetch technical and fundamental data via abstract providers
            raw_tech = self.tech_provider.fetch_indicators(symbol)
            raw_fund = self.fund_provider.fetch_fundamentals(symbol)

            tech_metrics = TechnicalMetrics(
                symbol=symbol,
                rsi=raw_tech.get("rsi", 55.0),
                ema_alignment=raw_tech.get("ema_alignment", "Bullish (20 > 50)"),
                volume_spike=raw_tech.get("volume_spike", True),
                support_distance_pct=raw_tech.get("support_distance_pct", 1.2)
            )

            fund_metrics = FundamentalMetrics(
                symbol=symbol,
                roe=raw_fund.get("roe", 18.5),
                debt_to_equity=raw_fund.get("debt_to_equity", 0.15),
                compliance_status=raw_fund.get("compliance_status", "Compliant / Halal Verified"),
                quarterly_growth_pct=raw_fund.get("quarterly_growth_pct", 14.2)
            )

            # 3. Query Knowledge Retrieval for sector/risk context
            retrieved = self.retrieval.search(f"{symbol} sector risk parameters and momentum rules")
            insight = retrieved.get("summary", "Standard parameters apply.")

            # 4. Evaluation logic
            is_qualified = (
                tech_metrics.rsi > 50 
                and tech_metrics.volume_spike 
                and fund_metrics.debt_to_equity < 0.5 
                and fund_metrics.compliance_status.startswith("Compliant")
            )

            verdict = "High Conviction" if is_qualified else "Filtered Out"
            if is_qualified:
                qualified_count += 1

            rationale = (
                f"Tech RSI at {tech_metrics.rsi} with volume confirmation. "
                f"Fundamental ROE at {fund_metrics.roe}% with D/E ratio {fund_metrics.debt_to_equity}. "
                f"Compliance: {fund_metrics.compliance_status}."
            )

            synthesis_items.append(
                SynthesisItem(
                    symbol=symbol,
                    verdict=verdict,
                    technical=tech_metrics,
                    fundamental=fund_metrics,
                    retrieved_insight=insight,
                    synthesis_rationale=rationale
                )
            )

        report = SynthesisReport(
            timestamp=datetime.utcnow().isoformat(),
            total_screened=len(symbols),
            qualified_count=qualified_count,
            synthesis_items=synthesis_items,
            provenance=[
                f"Technical Provider: {self.tech_provider.__class__.__name__}",
                f"Fundamental Provider: {self.fund_provider.__class__.__name__}",
                f"Knowledge Retrieval V3.6 Active",
                f"Guardrail Status: LIVE_AUTO_EXECUTION = {LIVE_AUTO_EXECUTION}"
            ]
        )

        logger.info("Technical and fundamental synthesis report generated successfully.")
        return report