from reliability_analytics.contracts.reliability_contract import ReliabilityScorecard

class ReliabilityMetricsCalculator:
    """
    Computes component-level operational reliability metrics (availability,
    successful refresh ratios, quality-pass ratios, failure frequency).
    """
    def calculate_scorecard(self, component_name: str, historical_runs: list) -> ReliabilityScorecard:
        if not historical_runs:
            return ReliabilityScorecard(
                component=component_name,
                availability_ratio=1.0,
                success_ratio=1.0,
                quality_pass_ratio=1.0,
                failure_frequency=0.0,
                mean_recovery_duration_seconds=0.0
            )

        total_runs = len(historical_runs)
        successes = sum(1 for r in historical_runs if r.get("status") == "PASS")
        quality_passes = sum(1 for r in historical_runs if r.get("quality_status") == "PASS")
        failures = total_runs - successes

        success_ratio = successes / total_runs
        quality_pass_ratio = quality_passes / total_runs
        failure_frequency = failures / total_runs

        return ReliabilityScorecard(
            component=component_name,
            availability_ratio=success_ratio,
            success_ratio=success_ratio,
            quality_pass_ratio=quality_pass_ratio,
            failure_frequency=failure_frequency,
            mean_recovery_duration_seconds=1.5  # Deterministic baseline estimate
        )
