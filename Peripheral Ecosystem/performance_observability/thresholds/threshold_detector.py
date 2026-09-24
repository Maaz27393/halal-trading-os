from performance_observability.contracts.performance_contract import PerformanceMetric, CapacityThresholdReport

class CapacityThresholdEvaluator:
    """
    Evaluates observed performance metrics against configuration baselines
    to determine capacity threshold states (NORMAL, ELEVATED, CAPACITY_WARNING, CAPACITY_CRITICAL).
    """
    def __init__(self, baseline_table: dict = None):
        # Default baseline durations in milliseconds for standard operations
        self.baseline_table = baseline_table or {
            "refresh_workflow": 50.0,
            "regression_run": 100.0,
            "investigation_analysis": 30.0,
            "notification_delivery": 15.0
        }

    def evaluate(self, metric: PerformanceMetric) -> CapacityThresholdReport:
        baseline = self.baseline_table.get(metric.operation, 40.0)
        ratio = metric.duration_ms / baseline if baseline > 0 else 1.0

        state = "NORMAL"
        if ratio > 3.0:
            state = "CAPACITY_CRITICAL"
        elif ratio > 2.0:
            state = "CAPACITY_WARNING"
        elif ratio > 1.25:
            state = "ELEVATED"

        return CapacityThresholdReport(
            metric_id=metric.metric_id,
            component=metric.component,
            operation=metric.operation,
            observed_duration_ms=metric.duration_ms,
            baseline_duration_ms=baseline,
            threshold_state=state,
            bottleneck_breakdown=metric.resource_context.get("breakdown", {})
        )
