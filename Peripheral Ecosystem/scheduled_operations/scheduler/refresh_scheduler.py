import uuid
import time
from datetime import datetime, timezone
from analytical_refresh.orchestrator.refresh_orchestrator import AnalyticalRefreshOrchestrator
from scheduled_operations.contracts.scheduled_contract import ScheduledRunTelemetry

class ScheduledOperationsEngine:
    """
    Manages the scheduled lifecycle of analytical refreshes, enforcing state progression,
    overlap protection, and non-execution safeguards.
    """
    def __init__(self):
        self.refresh_orchestrator = AnalyticalRefreshOrchestrator()
        self.is_running = False

    def run_job(self, trigger_type: str = "MANUAL") -> ScheduledRunTelemetry:
        if self.is_running:
            # Overlap prevention
            return ScheduledRunTelemetry(
                run_id="overlap-blocked",
                trigger_type=trigger_type,
                lifecycle_status="FAILED",
                overall_status="BLOCKED",
                error_information="Overlap prevention: A refresh job is already currently running."
            )

        self.is_running = True
        run_id = str(uuid.uuid4())[:8]
        scheduled_time = datetime.now(timezone.utc)
        start_time = datetime.now(timezone.utc)

        telemetry = ScheduledRunTelemetry(
            run_id=run_id,
            trigger_type=trigger_type,
            scheduled_timestamp=scheduled_time,
            actual_start=start_time,
            lifecycle_status="SCHEDULED"
        )

        try:
            # State: RUNNING
            telemetry.lifecycle_status = "RUNNING"
            
            # Execute Phase 23 Refresh Orchestrator (which handles export and pre-refresh validation)
            refresh_result = self.refresh_orchestrator.execute_refresh()

            # State: VALIDATING
            telemetry.lifecycle_status = "VALIDATING"
            telemetry.validation_results = refresh_result.validation_results

            if refresh_result.overall_status != "PASS":
                telemetry.lifecycle_status = "FAILED"
                telemetry.overall_status = "FAIL"
                telemetry.publication_result = False
                telemetry.error_information = refresh_result.failure_reason or "Validation check failed."
            else:
                # State: PUBLISHED
                telemetry.lifecycle_status = "PUBLISHED"
                telemetry.publication_result = True
                telemetry.feed_results = refresh_result.feeds_refreshed

                # State: COMPLETED
                telemetry.lifecycle_status = "COMPLETED"
                telemetry.overall_status = "PASS"

        except Exception as e:
            telemetry.lifecycle_status = "FAILED"
            telemetry.overall_status = "BLOCKED"
            telemetry.publication_result = False
            telemetry.error_information = f"Exception during scheduled execution: {str(e)}"

        finally:
            self.is_running = False
            end_time = datetime.now(timezone.utc)
            telemetry.actual_end = end_time
            telemetry.duration_seconds = (end_time - start_time).total_seconds()

        return telemetry
