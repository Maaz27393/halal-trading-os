import unittest
import uuid
from performance_observability.contracts.performance_contract import PerformanceMetric
from performance_observability.thresholds.threshold_detector import CapacityThresholdEvaluator
from performance_observability.analysis.bottleneck_analyzer import BottleneckAnalyzer
from performance_observability.collectors.evidence_adapter import PerformanceEvidenceAdapter

class TestPerformanceObservability(unittest.TestCase):
    def test_performance_pipeline(self):
        # 1. Test Bottleneck Analysis
        analyzer = BottleneckAnalyzer()
        steps = {"collection": 12.0, "validation": 8.0, "processing": 45.0, "reporting": 7.0, "delivery": 4.0}
        analysis = analyzer.analyze_steps(steps)
        self.assertEqual(analysis["primary_bottleneck"], "processing")
        self.assertEqual(analysis["total_duration_ms"], 76.0)

        # 2. Test Metric & Threshold Evaluation
        metric = PerformanceMetric(
            metric_id=str(uuid.uuid4())[:8],
            component="RefreshEngine",
            operation="refresh_workflow",
            duration_ms=160.0,  # Baseline is 50.0 -> Ratio 3.2 -> CAPACITY_CRITICAL
            status="DEGRADED",
            record_count=1500,
            resource_context={"breakdown": analysis["distribution_percentage"]},
            provenance="Phase32PerformanceCollector"
        )

        evaluator = CapacityThresholdEvaluator()
        report = evaluator.evaluate(metric)
        self.assertEqual(report.threshold_state, "CAPACITY_CRITICAL")

        # 3. Test Evidence Adaptation
        adapter = PerformanceEvidenceAdapter()
        k_obj = adapter.adapt_to_knowledge_object(report)
        self.assertEqual(k_obj.domain, "PERFORMANCE_OBSERVABILITY")
        self.assertIn("CAPACITY_CRITICAL", k_obj.content)
        self.assertTrue(k_obj.metadata["analysis_only"])

        print("\n--- PHASE 32 PERFORMANCE & CAPACITY REPORT ---")
        print(f"Metric ID: {metric.metric_id} | Operation: {metric.operation}")
        print(f"Observed Duration: {metric.duration_ms}ms | Baseline: {report.baseline_duration_ms}ms")
        print(f"Threshold State: {report.threshold_state}")
        print(f"Primary Bottleneck: {analysis['primary_bottleneck']} ({analysis['distribution_percentage']['processing']}%)")
        print(f"Evidence Object ID: {k_obj.object_id} | Security Boundary: Analysis Only = {k_obj.metadata['analysis_only']}")
        print("------------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
