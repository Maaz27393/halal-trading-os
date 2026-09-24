from predictive_risk.contracts.predictive_risk_contract import PredictiveRiskIndicator
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject

class PredictiveRiskEvidenceAdapter:
    """
    Converts predictive risk indicators into Phase 27-compatible KnowledgeObjects
    for downstream investigation, alerting, and Phase 18 governance review.
    """
    def adapt_to_knowledge_object(self, risk: PredictiveRiskIndicator) -> KnowledgeObject:
        return KnowledgeObject(
            object_id=f"risk-{risk.risk_id}",
            domain="PREDICTIVE_RISK",
            title=f"Predictive Risk Warning: {risk.risk_category} [{risk.risk_level}]",
            content=f"[{risk.risk_level}] Horizon: {risk.horizon}. Indicators converged: {risk.observed_indicators}. Historical patterns: {risk.historical_patterns}. Confidence: {risk.confidence_score}",
            provenance_source="Phase36PredictiveRiskDetector",
            metadata={
                "risk_id": risk.risk_id,
                "risk_category": risk.risk_category,
                "risk_level": risk.risk_level,
                "horizon": risk.horizon,
                "governance_status": risk.governance_status,
                "analysis_only": True
            }
        )
