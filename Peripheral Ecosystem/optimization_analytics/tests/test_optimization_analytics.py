import unittest
from optimization_analytics.candidates.detector import OptimizationCandidateDetector
from optimization_analytics.benchmarking.benchmarker import BenchmarkingFramework
from optimization_analytics.evidence.evidence_adapter import OptimizationEvidenceAdapter

class TestOptimizationAnalytics(unittest.TestCase):
    def test_optimization_pipeline(self):
        # 1. Test Candidate Detection
        detector = OptimizationCandidateDetector()
        candidate = detector.detect_candidate("RefreshWorkflow", "Excessive processing duration during market feed ingestion", 160.0, 150.0)
        self.assertEqual(candidate.target_component, "RefreshWorkflow")
        self.assertEqual(candidate.governance_status, "PENDING_HUMAN_REVIEW")
        self.assertGreater(candidate.estimated_impact_percentage, 0.0)

        # 2. Test Benchmarking Comparison
        benchmarker = BenchmarkingFramework()
        comparison = benchmarker.compare("RefreshWorkflow", 160.0, 95.0)
        self.assertEqual(comparison.status, "BENEFICIAL")
        self.assertGreater(comparison.improvement_percentage, 0.0)

        # 3. Test Evidence Adaptation
        adapter = OptimizationEvidenceAdapter()
        k_obj = adapter.adapt_to_knowledge_object(candidate)
        self.assertEqual(k_obj.domain, "OPTIMIZATION_ANALYTICS")
        self.assertIn("PENDING_HUMAN_REVIEW", k_obj.content)
        self.assertTrue(k_obj.metadata["analysis_only"])

        print("\n--- PHASE 33 OPTIMIZATION & EFFICIENCY REPORT ---")
        print(f"Candidate ID: {candidate.candidate_id} | Target: {candidate.target_component}")
        print(f"Estimated Impact: {candidate.estimated_impact_percentage}% | Confidence: {candidate.confidence_score}")
        print(f"Benchmark Comparison Status: {comparison.status} ({comparison.improvement_percentage}% improvement)")
        print(f"Evidence Object ID: {k_obj.object_id} | Governance Status: {candidate.governance_status}")
        print(f"Security Boundary: Analysis Only = {candidate.security_boundary['analysis_only']}")
        print("--------------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
