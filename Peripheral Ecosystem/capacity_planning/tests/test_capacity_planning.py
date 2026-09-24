import unittest
from capacity_planning.forecasting.forecaster import CapacityForecaster
from capacity_planning.utilization.analyzer import ResourceUtilizationAnalyzer
from capacity_planning.evidence.evidence_adapter import CapacityEvidenceAdapter

class TestCapacityPlanning(unittest.TestCase):
    def test_capacity_planning_pipeline(self):
        # 1. Test Resource Utilization Analysis
        util_analyzer = ResourceUtilizationAnalyzer()
        util_report = util_analyzer.analyze_utilization(65.0, 70.0, 15)
        self.assertEqual(util_report["status"], "HEALTHY")
        self.assertGreater(util_report["saturation_score"], 0.0)

        # 2. Test Capacity Forecasting
        forecaster = CapacityForecaster()
        forecast = forecaster.forecast_capacity("MarketDataIngestion", 1000.0, 0.65, 30) # 65% growth -> CAPACITY_RISK
        self.assertEqual(forecast.target_component, "MarketDataIngestion")
        self.assertIn(forecast.risk_state, ["CAPACITY_RISK", "CAPACITY_CRITICAL"])
        self.assertEqual(forecast.governance_status, "PENDING_HUMAN_REVIEW")

        # 3. Test Evidence Adaptation
        adapter = CapacityEvidenceAdapter()
        k_obj = adapter.adapt_to_knowledge_object(forecast)
        self.assertEqual(k_obj.domain, "CAPACITY_PLANNING")
        self.assertIn(forecast.risk_state, k_obj.content)
        self.assertTrue(k_obj.metadata["analysis_only"])

        print("\n--- PHASE 34 CAPACITY & RESOURCE PLANNING REPORT ---")
        print(f"Forecast ID: {forecast.forecast_id} | Component: {forecast.target_component}")
        print(f"Current Load: {forecast.current_workload_metric} -> Projected: {forecast.projected_workload_metric} ({forecast.time_horizon_days} days)")
        print(f"Risk State: {forecast.risk_state} | Saturation Score: {util_report['saturation_score']}")
        print(f"Evidence Object ID: {k_obj.object_id} | Governance Status: {forecast.governance_status}")
        print(f"Security Boundary: Analysis Only = {forecast.security_boundary['analysis_only']}")
        print("----------------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
