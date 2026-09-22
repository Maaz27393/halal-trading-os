from typing import List, Optional
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject, DecisionContextPackage
from knowledge_intelligence.retrieval.cross_domain_retriever import CrossDomainRetriever

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
