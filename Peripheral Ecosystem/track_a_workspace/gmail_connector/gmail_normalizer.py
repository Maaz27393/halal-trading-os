import logging
from typing import List, Dict, Any
from p7_expansion.agentic_refinement import ResearchDraft
from .gmail_adapter import GmailEmailItem

logger = logging.getLogger("A1GmailNormalizer")

class GmailIngestionNormalizer:
    """
    Normalizes filtered Gmail items into structured research drafts
    suitable for ingestion into the P7 multi-agent refinement pipeline.
    """

    @staticmethod
    def normalize_to_research_draft(email_item: GmailEmailItem) -> ResearchDraft:
        if email_item.has_execution_payload:
            raise ValueError("SECURITY HALT: Email contains forbidden execution payload.")

        title = f"Gmail Intelligence Ingestion: {email_item.subject}"
        content = f"""**Sender:** {email_item.sender}
**Timestamp:** {email_item.timestamp}
**Labels:** {', '.join(email_item.labels)}

**Extracted Body Snippet:**
{email_item.body_snippet}
"""
        provenance = [f"Gmail Message ID: {email_item.message_id}", f"Sender: {email_item.sender}"]
        
        return ResearchDraft(
            title=title,
            content=content,
            provenance_sources=provenance,
            author_agent="A1_Gmail_Ingestion_Module",
            has_execution_payload=False
        )