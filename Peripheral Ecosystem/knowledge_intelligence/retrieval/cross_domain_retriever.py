from typing import List, Optional
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject, DecisionContextPackage
from knowledge_intelligence.indexing.knowledge_indexer import KnowledgeIndexer

class CrossDomainRetriever:
    """
    Searches and filters knowledge objects across operational, quality,
    regression, and audit domains.
    """
    def __init__(self):
        self.indexer = KnowledgeIndexer()

    def search(self, query: str, domain_filter: Optional[str] = None) -> List[KnowledgeObject]:
        all_objects = self.indexer.build_index()
        results = []
        q_lower = query.lower()

        for obj in all_objects:
            if domain_filter and obj.domain != domain_filter:
                continue
            if q_lower in obj.title.lower() or q_lower in obj.content.lower() or q_lower in obj.domain.lower():
                results.append(obj)
        return results

class DecisionContextAssembler:
    """
    Assembles relevant retrieved evidence into a structured decision context package
    for investigation.
    """
    def __init__(self):
        self.retriever = CrossDomainRetriever()

    def assemble_context(self, investigation_id: str, query_topic: str) -> DecisionContextPackage:
        evidence = self.retriever.search(query_topic)
        
        facts = [e for e in evidence if e.domain in ["CONTROL_CENTER", "REGRESSION", "DATA_QUALITY"]]
        history = [e for e in evidence if e.domain in ["REFRESH", "AUDIT"]]

        derived = []
        if any(f.metadata.get("critical_failures", 0) > 0 for f in facts):
            derived.append("Warning: System reports active critical failures or non-zero error metrics.")
        else:
            derived.append("All inspected system domains report passing health and verified certification baselines.")

        return DecisionContextPackage(
            investigation_id=investigation_id,
            query_topic=query_topic,
            relevant_facts=facts,
            historical_records=history,
            derived_analysis=derived
        )
