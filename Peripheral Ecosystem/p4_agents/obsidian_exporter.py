import os
import logging
from datetime import datetime
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("ObsidianVaultExporter")

class ObsidianVaultExporter:
    """
    Exports structured P4 research artifacts into standardized Markdown notes
    within the local Obsidian vault structure.
    """

    def __init__(self, permission_gateway: PermissionGateway, vault_base_path: str):
        self.permission_gateway = permission_gateway
        self.vault_path = vault_base_path
        logger.info(f"ObsidianVaultExporter initialized with vault path: {vault_base_path}")

    def export_artifact(self, artifact_type: str, filename: str, content: str, caller_role: str = "analyst_agent") -> str:
        """
        Securely validate permissions and write a structured markdown file to the vault.
        """
        if not self.permission_gateway.verify_permission(caller_role, "WRITE"):
            raise PermissionError(f"Caller role '{caller_role}' lacks permission for 'WRITE' to vault.")

        # Determine target subfolder based on artifact type
        subfolder_map = {
            "premarket": "Pre-Market Briefings",
            "synthesis": "Technical Synthesis",
            "journal": "Trading Journals",
            "news_risk": "Risk Assessments",
            "post_market": "Post-Market Reports"
        }
        
        folder_name = subfolder_map.get(artifact_type, "Agent Research")
        target_dir = os.path.join(self.vault_path, "Peripheral Ecosystem", folder_name)
        
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Successfully exported {artifact_type} artifact to {file_path}")
        return file_path