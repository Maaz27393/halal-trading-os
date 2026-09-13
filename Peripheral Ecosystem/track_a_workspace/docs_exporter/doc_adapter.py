import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p7_expansion.agentic_refinement import ResearchDraft

logger = logging.getLogger("A2DocumentExporter")

class DocumentExportItem(BaseModel):
    title: str
    content: str
    author: str
    export_timestamp: str
    format_type: str = "MARKDOWN_DOCX"
    target_path: str

class A2DocumentExporter:
    """
    Track A.2: Secure Document Exporter Module.
    Converts P4–P7 research drafts and ingested feeds into formatted document files.
    Enforces strict WRITE/EXPORT permission gating via PermissionGateway.
    Maintains zero execution authority.
    """

    def __init__(self, permission_gateway: PermissionGateway, role: str = "analyst_agent", export_root: Optional[str] = None):
        self.permission_gateway = permission_gateway
        self._connected = False
        self._role = role
        self.export_root = export_root or "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem\\Refined Research"
        logger.info("A2DocumentExporter initialized with secure export boundary.")

    def connect(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """Establish secure boundary connection for document generation."""
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")
        
        if not self.permission_gateway.verify_permission(self._role, "WRITE"):
            logger.error(f"Document export connection denied: Role '{self._role}' lacks WRITE/EXPORT permission.")
            raise PermissionError(f"Role '{self._role}' lacks WRITE/EXPORT permission.")

        self._connected = True
        logger.info("A2DocumentExporter successfully connected (Export Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        """Return exporter health status."""
        return {
            "status": "HEALTHY" if self._connected else "DISCONNECTED",
            "exporter": "A2DocumentExporter",
            "live_auto_execution": LIVE_AUTO_EXECUTION,
            "permissions": "WRITE/EXPORT-ONLY"
        }

    def capabilities(self) -> List[str]:
        """Declare strict document export capabilities."""
        return [
            "format_research_draft",
            "generate_markdown_document",
            "export_to_vault",
            "verify_export_provenance"
        ]

    def export_draft(self, draft: ResearchDraft) -> DocumentExportItem:
        """
        Export a research draft into a formatted vault document.
        Enforces strict WRITE permission gating.
        """
        if not self._connected:
            raise ConnectionError("A2DocumentExporter is not connected.")

        if not self.permission_gateway.verify_permission(self._role, "WRITE"):
            raise PermissionError(f"Permission DENIED for role '{self._role}' on operation 'WRITE'.")

        if draft.has_execution_payload:
            raise ValueError("SECURITY HALT: Draft contains forbidden execution payload.")

        os.makedirs(self.export_root, exist_ok=True)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        safe_title = "".join([c if c.isalnum() else "_" for c in draft.title])[:50]
        filename = f"Export_{date_str}_{safe_title}.md"
        target_path = os.path.join(self.export_root, filename)

        formatted_content = f"""# {draft.title}

> **Author Agent:** {draft.author_agent}  
> **Export Timestamp:** {datetime.utcnow().isoformat()}  
> **Provenance Sources:** {', '.join(draft.provenance_sources)}  
> **Governance Status:** NON-CAUSAL RESEARCH (LIVE_AUTO_EXECUTION = FALSE)

---

{draft.content}
"""

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        logger.info(f"Successfully exported document to: {target_path}")

        return DocumentExportItem(
            title=draft.title,
            content=formatted_content,
            author=draft.author_agent,
            export_timestamp=datetime.utcnow().isoformat(),
            target_path=target_path
        )

    def disconnect(self) -> bool:
        """Disconnect and clear session boundary."""
        self._connected = False
        logger.info("A2DocumentExporter disconnected.")
        return True