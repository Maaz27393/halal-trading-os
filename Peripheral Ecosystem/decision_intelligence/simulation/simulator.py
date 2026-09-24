import uuid
from typing import Dict, List
from decision_intelligence.contracts.scenario_contract import ScenarioResult

class ScenarioSimulator:
    """
    Models hypothetical system changes and compares baseline vs projected metrics
    with sensitivity analysis.
    """
    def simulate_scenario(self, name: str, baseline: Dict[str, float], perturbations: Dict[str, float], assumptions: List[str]) -> ScenarioResult:
        projected = {}
        for k, v in baseline.items():
            factor = perturbations.get(k, 1.0)
            projected[k] = round(v * factor, 2)

        # Sensitivity rankings
        sensitivity = {k: round(abs(v - baseline.get(k, v)) / (baseline.get(k, 1.0)), 2) for k, v in projected.items()}

        return ScenarioResult(
            scenario_id=str(uuid.uuid4())[:8],
            scenario_name=name,
            baseline_metrics=baseline,
            projected_metrics=projected,
            assumptions=assumptions,
            sensitivity_rankings=sensitivity,
            confidence_score=0.85
        )
