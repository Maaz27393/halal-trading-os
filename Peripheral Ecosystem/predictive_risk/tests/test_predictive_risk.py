import unittest
from predictive_risk.detection.detector import PredictiveRiskDetector
from predictive_risk.evidence.evidence_adapter import PredictiveRiskEvidenceAdapter

class TestPredictiveRisk(unittest.TestCase):
    def test_predictive_risk_pipeline(self):
        detector = PredictiveRiskDetector()
        indicators = ["Latency increasing", "Error rate increasing", "Capacity saturation rising", "Pattern match found"]
        patterns = ["ProviderLatencySpikeToCapacitySaturation"]
        
        risk = detector.evaluate_risk(
            category="OPERATIONAL_DEGRADATION_RISK",
            domain="SYSTEM_WIDE",
            indicators=indicators,
            patterns=patterns,
            horizon="short_term",
            convergence_count=4
        )
        
        self.assertEqual(risk.risk_level, "CRITICAL")
        self.assertEqual(risk.horizon, "short_term")
        self.assertEqual(risk.governance_status, "PENDING_HUMAN_REVIEW")

        adapter = PredictiveRiskEvidenceAdapter()
        k_obj = adapter.adapt_to_knowledge_object(risk)
        self.assertEqual(k_obj.domain, "PREDICTIVE_RISK")
        self.assertIn("CRITICAL", k_obj.content)
        self.assertTrue(k_obj.metadata["analysis_only"])

        print("\n--- PHASE 36 PREDICTIVE RISK & EARLY WARNING REPORT ---")
        print(f"Risk ID: {risk.risk_id} | Category: {risk.risk_category}")
        print(f"Risk Level: {risk.risk_level} | Horizon: {risk.horizon} | Confidence: {risk.confidence_score}")
        print(f"Converged Indicators: {len(risk.observed_indicators)}")
        print(f"Evidence Object ID: {k_obj.object_id} | Governance Status: {risk.governance_status}")
        print(f"Security Boundary: Analysis Only = {risk.security_boundary['analysis_only']}")
        print("------------------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
