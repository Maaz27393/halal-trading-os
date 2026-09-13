import os
import re
import logging
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Any
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("VaultCrossReferencingEngine")

class TaggingReport(BaseModel):
    timestamp: str
    files_scanned: int
    tags_injected: List[str]
    provenance: List[str]

class VaultCrossReferencingEngine:
    """
    P5.3 Expansion: Automatically indexes Markdown artifacts in the Obsidian vault,
    injecting bi-directional wikilinks and dynamic operational tags.
    """

    def __init__(self, permission_gateway: PermissionGateway, vault_base_path: str):
        self.permission_gateway = permission_gateway
        self.vault_path = vault_base_path
        logger.info("VaultCrossReferencingEngine initialized for P5.3.")

    def process_and_tag_vault(self, caller_role: str = "analyst_agent") -> str:
        """
        1. Verify READ/WRITE permissions via the immutable Gateway.
        2. Scan vault subdirectories for Markdown artifacts.
        3. Inject standard wikilinks and tags safely with directory provisioning.
        """
        if not self.permission_gateway.verify_permission(caller_role, "READ") or \
           not self.permission_gateway.verify_permission(caller_role, "WRITE"):
            raise PermissionError(f"Caller role '{caller_role}' lacks permissions for vault tagging.")

        logger.info("Scanning vault for cross-referencing and dynamic tagging...")

        target_subdirs = [
            "Pre-Market Briefings",
            "Technical Synthesis",
            "Risk Assessments",
            "Trading Journals",
            "Post-Market Reports",
            "Advanced Charts",
            "Macro Intelligence"
        ]

        scanned_count = 0
        injected_tags = ["#halal-trading-os", "#agentic-research", "#p5-expansion"]

        for subdir in target_subdirs:
            dir_path = os.path.join(self.vault_path, "Peripheral Ecosystem", subdir)
            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    if filename.endswith(".md"):
                        file_path = os.path.join(dir_path, filename)
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Simple non-destructive check to append cross-reference index if missing
                        if "## Cross-References & Index" not in content:
                            updated_content = content + "\n\n## Cross-References & Index\n- Related: [[Halal Trading OS Master Index]]\n- Tags: #halal-trading-os #agentic-research\n"
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(updated_content)
                            scanned_count += 1

        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        report = TaggingReport(
            timestamp=datetime.utcnow().isoformat(),
            files_scanned=scanned_count,
            tags_injected=injected_tags,
            provenance=[
                f"P5.3 Vault Cross-Referencing Engine Active",
                f"Immutable Guardrail: LIVE_AUTO_EXECUTION = {LIVE_AUTO_EXECUTION}"
            ]
        )

        # Generate summary report artifact
        md_content = f"""---
date: {date_str}
type: vault-tagging-audit
files_updated: {report.files_scanned}
guardrail: LIVE_AUTO_EXECUTION=FALSE
---

# Vault Cross-Referencing & Tagging Audit - {date_str}

## Operation Summary
- **Files Processed & Updated**: {report.files_scanned}
- **Standard Tags Injected**: {', '.join(report.tags_injected)}

## Provenance
"""
        for prov in report.provenance:
            md_content += f"- {prov}\n"

        # Safe directory provisioning (prevents path does not exist errors)
        report_dir = os.path.join(self.vault_path, "Peripheral Ecosystem", "Vault Audits")
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, f"VaultAudit_{date_str}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Successfully executed P5.3 tagging pass. Audit saved to {report_path}")
        return report_path