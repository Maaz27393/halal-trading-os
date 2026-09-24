import unittest
from causal_intelligence.root_cause.detector import RootCauseDetector, DependencyInfluenceGraph
from causal_intelligence.evidence.evidence_adapter import CausalEvidenceAdapter

class TestCausalIntelligence(unittest.TestCase):
    def test_causal_intelligence_pipeline(self):
        # 1. Test Dependency Influence Graph
        graph = DependencyInfluenceGraph()
        graph_summary = graph.get_graph_summary()
        self.assertEqual(graph_summary["edge_count"], 5)

        # 2. Test Root Cause Detection
        detector = RootCauseDetector()
        observations = [
            "Provider latency increased by 87%",
            "Processing duration spiked by 35%",
            "Capacity saturation reached 82.08%"
        ]
        correlated = ["HIGH_LOAD regime detected", "Predictive risk escalated to CRITICAL"]
        contradictory = ["Zero packet loss reported at network gateway"]

        candidate = detector.detect_root_cause(
            domain="SYSTEM_WIDE",
            cause="ProviderLatencySpikeToCapacitySaturation",
            observations=observations,
            correlated=correlated,
            contradictory=contradictory,
            confidence=0.82
        )

        self.assertEqual(candidate.relationship_type, "CANDIDATE_CAUSE")
        self.assertEqual(candidate.investigation_status, "PENDING_HUMAN_REVIEW")
        self.assertEqual(candidate.confidence_score, 0.82)

        # 3. Test Evidence Adaptation
        adapter = CausalEvidenceAdapter()
        k_obj = adapter.adapt_to_knowledge_object(candidate)
        self.assertEqual(k_obj.domain, "CAUSAL_INTELLIGENCE")
        self.assertIn("CANDIDATE_CAUSE", k_obj.content)
        self.assertTrue(k_obj.metadata["analysis_only"])

        print("\n--- PHASE 38 CAUSAL ANALYSIS REPORT ---")
        print(f"Root Cause ID: {candidate.root_cause_id} | Cause: {candidate.candidate_cause}")
        print(f"Relationship Type: {candidate.relationship_type} | Confidence: {candidate.confidence_score}")
        print(f"Graph Edges Tracked: {graph_summary['edge_count']} with Provenance")
        print(f"Evidence Object ID: {k_obj.object_id} | Investigation Status: {candidate.investigation_status}")
        print(f"Security Boundary: Analysis Only = {candidate.security_boundary['analysis_only']}")
        print("------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
