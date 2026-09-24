import uuid
from reliability_analytics.contracts.reliability_contract import AnomalyEvent

class AnomalyDetector:
    """
    Detects statistical deviations between observed metrics and historical baselines,
    categorizing states into NORMAL, UNUSUAL, ANOMALOUS, or EARLY_WARNING.
    """
    def detect_anomaly(self, component: str, metric_name: str, observed_value: float, baseline_expected: float) -> AnomalyEvent:
        deviation = abs(observed_value - baseline_expected) / (baseline_expected if baseline_expected != 0 else 1.0)

        severity = "NORMAL"
        desc = f"Metric {metric_name} is operating within normal parameters."

        if deviation > 0.50:
            severity = "EARLY_WARNING"
            desc = f"Severe deviation detected on {metric_name} ({observed_value} vs baseline {baseline_expected}). Early degradation signal."
        elif deviation > 0.25:
            severity = "ANOMALOUS"
            desc = f"Significant statistical deviation detected on {metric_name} ({observed_value} vs baseline {baseline_expected})."
        elif deviation > 0.10:
            severity = "UNUSUAL"
            desc = f"Slight deviation detected on {metric_name} ({observed_value} vs baseline {baseline_expected})."

        return AnomalyEvent(
            anomaly_id=str(uuid.uuid4())[:8],
            component=component,
            metric_name=metric_name,
            observed_value=observed_value,
            baseline_expected=baseline_expected,
            deviation_score=round(deviation, 3),
            severity_state=severity,
            description=desc
        )
