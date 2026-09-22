import unittest
from knowledge_intelligence.indexing.knowledge_indexer import KnowledgeIndexer
from knowledge_intelligence.retrieval.cross_domain_retriever import CrossDomainRetriever
from knowledge_intelligence.context.decision_assembler import DecisionContextAssembler

class TestKnowledgeIntelligence(unittest.TestCase):
    def test_knowledge_pipeline(self):
        indexer = KnowledgeIndexer()
        objects = indexer.build_index()
        self.assertGreater(len(objects), 0)

        retriever = CrossDomainRetriever()
        results = retriever.search("Status")
        self.assertGreater(len(results), 0)

        assembler = DecisionContextAssembler()
        package = assembler.assemble_context(investigation_id="inv-001", query_topic="Regression")
        
        self.assertEqual(package.investigation_id, "inv-001")
        self.assertGreater(len(package.relevant_facts), 0)
        self.assertEqual(package.safety_guarantee, "STRICTLY_READ_ONLY_EVIDENCE")

        print("\n--- PHASE 27 KNOWLEDGE INTELLIGENCE REPORT ---")
        print(f"Investigation ID: {package.investigation_id}")
        print(f"Query Topic: {package.query_topic}")
        print(f"Indexed Facts Found: {len(package.relevant_facts)}")
        print(f"Historical Records Found: {len(package.historical_records)}")
        print(f"Derived Analysis: {package.derived_analysis}")
        print("-----------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
