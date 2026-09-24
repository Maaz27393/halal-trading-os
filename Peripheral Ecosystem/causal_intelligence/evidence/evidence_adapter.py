from causal_intelligence.contracts.root_cause_contract import RootCauseCandidate
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject

class CausalEvidenceAdapter:
    """
    Converts root-cause candidates into Phase 27-compatible KnowledgeObjects
    for downstream Phase 28 investigation and Phase 29 notification.
    """
    def adapt_to_knowledge_object(self, candidate: RootCauseCandidate) -> KnowledgeObject:
        return KnowledgeObject(
            object_id=f"rc-{candidate.root_cause_id}",
            domain="CAUSAL_INTELLIGENCE",
            title=f"Root-Cause Candidate: {candidate.candidate_cause} [{candidate.relationship_type}]",
            content=f"[{candidate.relationship_type}] Affected Domain: {candidate.affected_domain}. Cause: {candidate.candidate_cause}. Observations: {candidate.supporting_observations}. Correlated: {candidate.correlated_signals}. Confidence: {candidate.confidence_score}",
            provenance_source="Phase38RootCauseDetector",
            metadata={
                "root_cause_id": candidate.root_cause_id,
                "affected_domain": candidate.affected_domain,
                "relationship_type": candidate.relationship_type,
                "investigation_status": candidate.investigation_status,
                "analysis_only": True
            }
        )
