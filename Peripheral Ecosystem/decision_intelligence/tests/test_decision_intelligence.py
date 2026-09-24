import unittest
from decision_intelligence.simulation.simulator import ScenarioSimulator
from decision_intelligence.evidence.evidence_adapter import ScenarioEvidenceAdapter

class TestDecisionIntelligence(unittest.TestCase):
    def test_decision_intelligence_pipeline(self):
        simulator = ScenarioSimulator()
        baseline = {"workload": 1000.0, "latency_ms": 40.0, "saturation_pct": 57.0}
        perturbations = {"workload": 1.65, "latency_ms": 1.87, "saturation_pct": 1.44}
        assumptions = ["Provider latency increases by 87%", "Workload surges by 65%"]

        result = simulator.simulate_scenario(
            name="CombinedCapacitySurge",
            baseline=baseline,
            perturbations=perturbations,
            assumptions=assumptions
        )

        self.assertEqual(result.scenario_name, "CombinedCapacitySurge")
        self.assertEqual(result.projected_metrics["workload"], 1650.0)
        self.assertEqual(result.governance_status, "PENDING_HUMAN_REVIEW")

        adapter = ScenarioEvidenceAdapter()
        k_obj = adapter.adapt_to_knowledge_object(result)
        self.assertEqual(k_obj.domain, "DECISION_INTELLIGENCE")
        self.assertIn("HYPOTHETICAL", k_obj.content)
        self.assertTrue(k_obj.metadata["hypothetical_analysis"])

        print("\n--- PHASE 37 DECISION INTELLIGENCE REPORT ---")
        print(f"Scenario ID: {result.scenario_id} | Name: {result.scenario_name}")
        print(f"Baseline Metrics: {result.baseline_metrics}")
        print(f"Projected Metrics: {result.projected_metrics}")
        print(f"Sensitivity Rankings: {result.sensitivity_rankings}")
        print(f"Evidence Object ID: {k_obj.object_id} | Governance Status: {result.governance_status}")
        print(f"Security Boundary: Analysis Only = {result.security_boundary['analysis_only']} | Hypothetical = True")
        print("-----------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
