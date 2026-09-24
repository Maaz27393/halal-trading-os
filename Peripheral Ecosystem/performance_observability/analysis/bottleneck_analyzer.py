from typing import Dict, Any

class BottleneckAnalyzer:
    """
    Analyzes granular time-spent distributions across workflow steps
    (collection, validation, processing, reporting, delivery) to pinpoint bottlenecks.
    """
    def analyze_steps(self, steps: Dict[str, float]) -> Dict[str, Any]:
        total_duration = sum(steps.values())
        if total_duration == 0:
            return {"primary_bottleneck": "NONE", "distribution": {}}

        breakdown = {step: round((duration / total_duration) * 100, 2) for step, duration in steps.items()}
        primary_bottleneck = max(steps, key=steps.get)

        return {
            "total_duration_ms": total_duration,
            "primary_bottleneck": primary_bottleneck,
            "distribution_percentage": breakdown
        }
