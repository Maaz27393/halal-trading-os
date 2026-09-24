import unittest
from pattern_intelligence.mining.miner import PatternMiner
from pattern_intelligence.regimes.analyzer import RegimeStateAnalyzer
from pattern_intelligence.evidence.evidence_adapter import PatternEvidenceAdapter

class TestPatternIntelligence(unittest.TestCase):
    def test_pattern_intelligence_pipeline(self):
        # 1. Test Regime Classification
        regime_analyzer = RegimeStateAnalyzer()
        regime = regime_analyzer.classify_regime(0.02, 120.0, 75.0)
        self.assertEqual(regime, "HIGH_LOAD")

        # 2. Test Pattern Mining
        miner = PatternMiner()
        pattern = miner.mine_pattern(
            domains=["RELIABILITY_ANALYTICS", "PERFORMANCE_OBSERVABILITY", "CAPACITY_PLANNING"],
            name="ProviderLatencySpikeToCapacitySaturation",
            desc="Provider degradation precedes processing latency spike and high resource saturation.",
            occurrences=14,
            confidence=0.88,
            regime=regime
        )
        self.assertEqual(pattern.regime_state, "HIGH_LOAD")
        self.assertEqual(pattern.governance_status, "PENDING_HUMAN_REVIEW")

        # 3. Test Evidence Adaptation
        adapter = PatternEvidenceAdapter()
        k_obj = adapter.adapt_to_knowledge_object(pattern)
        self.assertEqual(k_obj.domain, "PATTERN_INTELLIGENCE")
        self.assertIn("HIGH_LOAD", k_obj.content)
        self.assertTrue(k_obj.metadata["analysis_only"])

        print("\n--- PHASE 35 ADAPTIVE INTELLIGENCE REPORT ---")
        print(f"Pattern ID: {pattern.pattern_id} | Name: {pattern.pattern_name}")
        print(f"Source Domains: {pattern.source_domains}")
        print(f"Regime State: {pattern.regime_state} | Occurrences: {pattern.occurrence_count} | Confidence: {pattern.confidence_score}")
        print(f"Evidence Object ID: {k_obj.object_id} | Governance Status: {pattern.governance_status}")
        print(f"Security Boundary: Analysis Only = {pattern.security_boundary['analysis_only']}")
        print("-----------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
