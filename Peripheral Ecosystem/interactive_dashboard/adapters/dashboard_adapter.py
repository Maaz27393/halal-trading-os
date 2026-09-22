from datetime import datetime, timezone
from master_cli.cli.master_controller import MasterEcosystemController
from interactive_dashboard.contracts.dashboard_contract import DashboardState

class DashboardAdapter:
    """
    Adapter bridging the interactive dashboard UI to the Master Ecosystem Controller
    and underlying certified domains.
    """
    def __init__(self):
        self.controller = MasterEcosystemController()

    def fetch_dashboard_state(self) -> DashboardState:
        # Execute Master CLI queries to gather clean certified state
        status_audit = self.controller.execute_command("STATUS")
        cert_audit = self.controller.execute_command("CERTIFY")
        refresh_audit = self.controller.execute_command("REFRESH")
        audit_cmd = self.controller.execute_command("AUDIT")

        status_details = status_audit.details
        cert_details = cert_audit.details
        refresh_details = refresh_audit.details

        return DashboardState(
            system_overview={
                "system_status": status_details.get("system_status", "UNKNOWN"),
                "regression_status": status_details.get("regression_status", "UNKNOWN"),
                "data_quality_status": status_details.get("data_quality_status", "UNKNOWN"),
                "critical_failures": status_details.get("critical_failures", 0)
            },
            provider_health=status_details.get("providers", {}),
            data_quality={
                "status": status_details.get("data_quality_status", "UNKNOWN"),
                "freshness": "FRESH",
                "completeness": "100%"
            },
            governance={
                "read_only": True,
                "live_auto_execution": False,
                "order_capability": "NONE",
                "execution_authority": "NONE",
                "governance_mode": "READ_ONLY"
            },
            refresh_operations={
                "last_run_id": refresh_details.get("run_id", "N/A"),
                "lifecycle_status": refresh_details.get("lifecycle_status", "N/A"),
                "publication_result": refresh_details.get("publication_result", False),
                "feeds_refreshed": refresh_details.get("feed_results", [])
            },
            certification={
                "overall_status": cert_details.get("overall_status", "UNKNOWN"),
                "domains": cert_details.get("domains", {}),
                "failures": cert_details.get("failures", [])
            },
            audit_trail=[
                {
                    "command": log.command,
                    "status": log.status,
                    "timestamp": log.timestamp.isoformat(),
                    "audit_id": log.audit_id
                }
                for log in self.controller.audit_history
            ]
        )
