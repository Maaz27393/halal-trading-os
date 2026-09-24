from capacity_planning.contracts.capacity_contract import CapacityForecast
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject

class CapacityEvidenceAdapter:
    """
    Converts capacity forecasts into Phase 27 KnowledgeObjects for downstream
    investigation, notification, and Phase 18 change governance review.
    """
    def adapt_to_knowledge_object(self, forecast: CapacityForecast) -> KnowledgeObject:
        return KnowledgeObject(
            object_id=f"cap-{forecast.forecast_id}",
            domain="CAPACITY_PLANNING",
            title=f"Capacity Forecast Alert: {forecast.target_component} [{forecast.risk_state}]",
            content=f"[{forecast.risk_state}] Component {forecast.target_component} current load: {forecast.current_workload_metric}. Projected load in {forecast.time_horizon_days} days: {forecast.projected_workload_metric}. Confidence: {forecast.confidence_score}",
            provenance_source="Phase34CapacityForecaster",
            metadata={
                "forecast_id": forecast.forecast_id,
                "target_component": forecast.target_component,
                "risk_state": forecast.risk_state,
                "projected_workload_metric": forecast.projected_workload_metric,
                "governance_status": forecast.governance_status,
                "analysis_only": True
            }
        )
