class RegimeStateAnalyzer:
    """
    Classifies the current system operational state into deterministic regimes:
    NORMAL, DEGRADED, HIGH_LOAD, CAPACITY_RISK, or RECOVERY.
    """
    def classify_regime(self, error_rate: float, latency_ms: float, saturation_score: float) -> str:
        if error_rate > 0.20 or latency_ms > 200.0:
            return "DEGRADED"
        elif saturation_score > 85.0:
            return "CAPACITY_RISK"
        elif saturation_score > 70.0:
            return "HIGH_LOAD"
        elif error_rate > 0.05:
            return "RECOVERY"
        else:
            return "NORMAL"
