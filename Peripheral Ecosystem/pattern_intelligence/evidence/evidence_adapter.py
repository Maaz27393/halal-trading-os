from pattern_intelligence.contracts.pattern_contract import OperationalPattern
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject

class PatternEvidenceAdapter:
    """
    Converts discovered operational patterns into Phase 27-compatible KnowledgeObjects
    for downstream investigation, notification, and Phase 18 governance review.
    """
    def adapt_to_knowledge_object(self, pattern: OperationalPattern) -> KnowledgeObject:
        return KnowledgeObject(
            object_id=f"pat-{pattern.pattern_id}",
            domain="PATTERN_INTELLIGENCE",
            title=f"Operational Pattern Discovered: {pattern.pattern_name} [{pattern.regime_state}]",
            content=f"[{pattern.regime_state}] Pattern '{pattern.pattern_name}' observed {pattern.occurrence_count} times across domains {pattern.source_domains}. Confidence: {pattern.confidence_score}. Description: {pattern.description}",
            provenance_source="Phase35PatternMiner",
            metadata={
                "pattern_id": pattern.pattern_id,
                "source_domains": pattern.source_domains,
                "regime_state": pattern.regime_state,
                "confidence_score": pattern.confidence_score,
                "governance_status": pattern.governance_status,
                "analysis_only": True
            }
        )
