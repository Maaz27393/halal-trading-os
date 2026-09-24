from performance_observability.contracts.performance_contract import CapacityThresholdReport
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject

class PerformanceEvidenceAdapter:
    """
    Converts performance capacity threshold reports into Phase 27-compatible KnowledgeObjects
    for downstream investigation and incident reporting.
    """
    def adapt_to_knowledge_object(self, report: CapacityThresholdReport) -> KnowledgeObject:
        return KnowledgeObject(
            object_id=f"perf-{report.metric_id}",
            domain="PERFORMANCE_OBSERVABILITY",
            title=f"Capacity Alert: {report.component} ({report.operation}) - {report.threshold_state}",
            content=f"[{report.threshold_state}] Operation {report.operation} took {report.observed_duration_ms}ms (Baseline: {report.baseline_duration_ms}ms). Bottlenecks: {report.bottleneck_breakdown}",
            provenance_source="Phase32CapacityEvaluator",
            metadata={
                "metric_id": report.metric_id,
                "component": report.component,
                "operation": report.operation,
                "threshold_state": report.threshold_state,
                "observed_duration_ms": report.observed_duration_ms,
                "analysis_only": True
            }
        )
