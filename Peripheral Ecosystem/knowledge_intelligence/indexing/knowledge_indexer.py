import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from knowledge_intelligence.contracts.knowledge_contract import KnowledgeObject
from master_cli.cli.master_controller import MasterEcosystemController

class KnowledgeIndexer:
    """
    Indexes Phase 20-26 peripheral outputs into searchable, timestamped knowledge objects
    preserving full source provenance.
    """
    def __init__(self):
        self.controller = MasterEcosystemController()

    def build_index(self) -> List[KnowledgeObject]:
        objects = []
        
        # 1. Capture Control Center Status
        status_audit = self.controller.execute_command("STATUS")
        status_details = status_audit.details
        objects.append(KnowledgeObject(
            object_id=f"cc-{status_audit.audit_id}",
            domain="CONTROL_CENTER",
            title="Ecosystem Operational Status Snapshot",
            content=f"System Status: {status_details.get('system_status')}, Regression: {status_details.get('regression_status')}, Critical Failures: {status_details.get('critical_failures')}",
            provenance_source="OperationalControlCenterAggregator",
            metadata=status_details
        ))

        # 2. Capture Regression Certification Report
        cert_audit = self.controller.execute_command("CERTIFY")
        cert_details = cert_audit.details
        objects.append(KnowledgeObject(
            object_id=f"reg-{cert_audit.audit_id}",
            domain="REGRESSION",
            title="System Regression Certification Report",
            content=f"Overall Status: {cert_details.get('overall_status')}, Domains Verified: {list(cert_details.get('domains', {}).keys())}",
            provenance_source="SystemRegressionOrchestrator",
            metadata=cert_details
        ))

        # 3. Capture Refresh Telemetry
        refresh_audit = self.controller.execute_command("REFRESH")
        refresh_details = refresh_audit.details
        objects.append(KnowledgeObject(
            object_id=f"ref-{refresh_audit.audit_id}",
            domain="REFRESH",
            title="Analytical Feed Refresh & Publication Record",
            content=f"Run ID: {refresh_details.get('run_id')}, Lifecycle Status: {refresh_details.get('lifecycle_status')}, Publication: {refresh_details.get('publication_result')}",
            provenance_source="AnalyticalRefreshOrchestrator",
            metadata=refresh_details
        ))

        # 4. Capture Audit History Records
        for log in self.controller.audit_history:
            objects.append(KnowledgeObject(
                object_id=f"aud-{log.audit_id}",
                domain="AUDIT",
                title=f"Master CLI Command Execution: {log.command}",
                content=f"Command {log.command} executed with status {log.status}.",
                provenance_source="MasterEcosystemController",
                metadata={"command": log.command, "status": log.status}
            ))

        return objects
