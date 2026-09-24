from decision_intelligence.contracts.scenario_contract import ScenarioResult
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject

class ScenarioEvidenceAdapter:
    """
    Converts scenario simulation results into Phase 27-compatible KnowledgeObjects
    for downstream investigation, alerting, and Phase 18 governance review.
    """
    def adapt_to_knowledge_object(self, result: ScenarioResult) -> KnowledgeObject:
        return KnowledgeObject(
            object_id=f"dec-{result.scenario_id}",
            domain="DECISION_INTELLIGENCE",
            title=f"Scenario Simulation: {result.scenario_name} [HYPOTHETICAL]",
            content=f"[HYPOTHETICAL ANALYSIS] Scenario '{result.scenario_name}' baseline: {result.baseline_metrics} -> projected: {result.projected_metrics}. Assumptions: {result.assumptions}. Confidence: {result.confidence_score}",
            provenance_source="Phase37ScenarioSimulator",
            metadata={
                "scenario_id": result.scenario_id,
                "scenario_name": result.scenario_name,
                "hypothetical_analysis": True,
                "governance_status": result.governance_status,
                "analysis_only": True
            }
        )
