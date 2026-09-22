import uuid
from typing import List
from investigation_reporting.contracts.investigation_contract import EvidenceItem
from knowledge_intelligence.indexing.knowledge_indexer import KnowledgeIndexer

class EvidenceCollector:
    """
    Harvests multi-domain evidence from Phase 27 knowledge objects and underlying
    certified peripheral outputs, preserving complete provenance.
    """
    def __init__(self):
        self.indexer = KnowledgeIndexer()

    def collect_evidence(self) -> List[EvidenceItem]:
        knowledge_objects = self.indexer.build_index()
        evidence_items = []

        for obj in knowledge_objects:
            evidence_items.append(EvidenceItem(
                evidence_id=f"ev-{obj.object_id}",
                source_domain=obj.domain,
                timestamp=obj.timestamp,
                content=obj.content,
                provenance=obj.provenance_source,
                raw_metadata=obj.metadata
            ))

        return evidence_items
