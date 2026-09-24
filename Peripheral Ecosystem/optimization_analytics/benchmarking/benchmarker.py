import uuid
from optimization_analytics.contracts.optimization_contract import BenchmarkComparison

class BenchmarkingFramework:
    """
    Executes reproducible before/after comparison framework to verify whether
    applied changes result in performance improvements or regressions.
    """
    def compare(self, component: str, baseline_ms: float, optimized_ms: float) -> BenchmarkComparison:
        diff = baseline_ms - optimized_ms
        improvement = round((diff / baseline_ms) * 100, 2) if baseline_ms > 0 else 0.0

        status = "BENEFICIAL" if improvement > 0 else ("REGRESSION" if improvement < 0 else "NEUTRAL")

        return BenchmarkComparison(
            benchmark_id=str(uuid.uuid4())[:8],
            component=component,
            baseline_ms=baseline_ms,
            optimized_ms=optimized_ms,
            improvement_percentage=improvement,
            status=status
        )
