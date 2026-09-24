from typing import Dict, Any
from reliability_analytics.contracts.reliability_contract import AnomalyEvent
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject

class ReliabilityEvidenceAdapter:
    """
    Converts detected anomaly events into Phase 27-compatible KnowledgeObjects
    so they can be consumed by the investigation and incident reporting engine.
    """
    def adapt_to_knowledge_object(self, anomaly: AnomalyEvent) -> KnowledgeObject:
        return KnowledgeObject(
            object_id=f"anom-{anomaly.anomaly_id}",
            domain="RELIABILITY_ANALYTICS",
            title=f"Anomaly Alert: {anomaly.component} - {anomaly.metric_name}",
            content=f"[{anomaly.severity_state}] {anomaly.description} (Deviation: {anomaly.deviation_score * 100}%)",
            provenance_source="Phase31AnomalyDetector",
            metadata={
                "anomaly_id": anomaly.anomaly_id,
                "component": anomaly.component,
                "metric_name": anomaly.metric_name,
                "severity": anomaly.severity_state,
                "deviation_score": anomaly.deviation_score,
                "analysis_only": True
            }
        )
