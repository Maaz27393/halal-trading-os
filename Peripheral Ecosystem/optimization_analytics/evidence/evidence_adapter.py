from optimization_analytics.contracts.optimization_contract import OptimizationCandidate
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject

class OptimizationEvidenceAdapter:
    """
    Converts optimization candidates into Phase 27 KnowledgeObjects and links
    them to Phase 18 change governance workflows for human review.
    """
    def adapt_to_knowledge_object(self, candidate: OptimizationCandidate) -> KnowledgeObject:
        return KnowledgeObject(
            object_id=f"opt-{candidate.candidate_id}",
            domain="OPTIMIZATION_ANALYTICS",
            title=f"Optimization Opportunity: {candidate.target_component} ({candidate.estimated_impact_percentage}% Impact)",
            content=f"[PENDING_HUMAN_REVIEW] Bottleneck: {candidate.bottleneck_description}. Baseline: {candidate.baseline_duration_ms}ms -> Projected: {candidate.projected_duration_ms}ms. Confidence: {candidate.confidence_score}",
            provenance_source="Phase33OptimizationDetector",
            metadata={
                "candidate_id": candidate.candidate_id,
                "target_component": candidate.target_component,
                "estimated_impact_percentage": candidate.estimated_impact_percentage,
                "governance_status": candidate.governance_status,
                "analysis_only": True
            }
        )
