import uuid
from datetime import datetime, timezone
from operational_control_center.aggregators.control_center_aggregator import OperationalControlCenterAggregator
from scheduled_operations.scheduler.refresh_scheduler import ScheduledOperationsEngine
from system_validation.runners.regression_runner import SystemRegressionOrchestrator
from master_cli.contracts.cli_contract import AuditLogRecord

class MasterEcosystemController:
    """
    Central dispatch controller for the peripheral ecosystem. Coordinates
    Phase 20 (Regression), Phase 21 (Control Center), and Phase 24 (Scheduler)
    under a unified audit logging wrapper.
    """
    def __init__(self):
        self.control_center = OperationalControlCenterAggregator()
        self.scheduler = ScheduledOperationsEngine()
        self.regression_orchestrator = SystemRegressionOrchestrator()
        self.audit_history = []

    def execute_command(self, command: str) -> AuditLogRecord:
        audit_id = str(uuid.uuid4())[:8]
        cmd_upper = command.upper().strip()
        status = "PASS"
        details = {}

        try:
            if cmd_upper == "STATUS":
                summary = self.control_center.get_ecosystem_summary()
                details = {
                    "system_status": summary.system_status,
                    "regression_status": summary.regression_status,
                    "data_quality_status": summary.data_quality_status,
                    "providers": summary.providers,
                    "critical_failures": summary.critical_failures
                }
            elif cmd_upper == "REFRESH":
                telemetry = self.scheduler.run_job(trigger_type="CLI_MANUAL")
                details = {
                    "run_id": telemetry.run_id,
                    "lifecycle_status": telemetry.lifecycle_status,
                    "publication_result": telemetry.publication_result,
                    "feed_results": telemetry.feed_results
                }
                if telemetry.overall_status != "PASS":
                    status = "FAIL"
            elif cmd_upper == "CERTIFY":
                report = self.regression_orchestrator.generate_certification_report()
                details = {
                    "overall_status": report.overall_status,
                    "domains": report.domains,
                    "failures": report.failures
                }
                if report.overall_status != "PASS":
                    status = "FAIL"
            elif cmd_upper == "AUDIT":
                details = {
                    "total_audits_recorded": len(self.audit_history),
                    "last_commands": [log.command for log in self.audit_history[-5:]]
                }
            else:
                status = "BLOCKED"
                details = {"error": f"Unknown command: {command}. Valid commands: STATUS, REFRESH, CERTIFY, AUDIT"}

        except Exception as e:
            status = "BLOCKED"
            details = {"error": str(e)}

        record = AuditLogRecord(
            audit_id=audit_id,
            command=cmd_upper,
            status=status,
            details=details
        )
        self.audit_history.append(record)
        return record
