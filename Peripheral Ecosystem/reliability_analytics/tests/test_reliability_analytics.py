import unittest
from reliability_analytics.metrics.scorecard import ReliabilityMetricsCalculator
from reliability_analytics.detection.detector import AnomalyDetector
from reliability_analytics.adapters.evidence_adapter import ReliabilityEvidenceAdapter

class TestReliabilityAnalytics(unittest.TestCase):
    def test_reliability_pipeline(self):
        # 1. Test Metrics Calculator
        calc = ReliabilityMetricsCalculator()
        history = [{"status": "PASS", "quality_status": "PASS"}, {"status": "PASS", "quality_status": "PASS"}, {"status": "FAIL", "quality_status": "WARN"}]
        scorecard = calc.calculate_scorecard("MarketDataFeed", history)
        self.assertEqual(scorecard.component, "MarketDataFeed")
        self.assertAlmostEqual(scorecard.success_ratio, 0.666, places=2)

        # 2. Test Anomaly Detection
        detector = AnomalyDetector()
        # Normal
        norm_anomaly = detector.detect_anomaly("ExecutionGateway", "latency_ms", 105.0, 100.0)
        self.assertEqual(norm_anomaly.severity_state, "NORMAL")

        # Early Warning / Anomalous
        warn_anomaly = detector.detect_anomaly("ExecutionGateway", "latency_ms", 180.0, 100.0)
        self.assertIn(warn_anomaly.severity_state, ["ANOMALOUS", "EARLY_WARNING"])

        # 3. Test Evidence Adapter
        adapter = ReliabilityEvidenceAdapter()
        k_obj = adapter.adapt_to_knowledge_object(warn_anomaly)
        self.assertEqual(k_obj.domain, "RELIABILITY_ANALYTICS")
        self.assertIn("EARLY_WARNING", k_obj.content)
        self.assertTrue(k_obj.metadata["analysis_only"])

        print("\n--- PHASE 31 RELIABILITY & ANOMALY REPORT ---")
        print(f"Scorecard Success Ratio: {scorecard.success_ratio:.2f}")
        print(f"Detected Anomaly State: {warn_anomaly.severity_state} (Deviation: {warn_anomaly.deviation_score})")
        print(f"Evidence Object ID: {k_obj.object_id} | Domain: {k_obj.domain}")
        print(f"Security Boundary: Analysis Only = {k_obj.metadata['analysis_only']}")
        print("-----------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
