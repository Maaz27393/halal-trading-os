import uuid
from optimization_analytics.contracts.optimization_contract import OptimizationCandidate

class OptimizationCandidateDetector:
    """
    Detects repeated bottlenecks from telemetry and generates optimization candidates
    with estimated impact and confidence scores, pending human review.
    """
    def detect_candidate(self, component: str, bottleneck_desc: str, baseline_ms: float, observed_ms: float) -> OptimizationCandidate:
        projected_ms = max(baseline_ms * 0.7, observed_ms * 0.6)
        impact = round(((observed_ms - projected_ms) / observed_ms) * 100, 2) if observed_ms > 0 else 0.0

        return OptimizationCandidate(
            candidate_id=str(uuid.uuid4())[:8],
            target_component=component,
            bottleneck_description=bottleneck_desc,
            baseline_duration_ms=baseline_ms,
            projected_duration_ms=round(projected_ms, 2),
            estimated_impact_percentage=impact,
            confidence_score=0.85
        )
