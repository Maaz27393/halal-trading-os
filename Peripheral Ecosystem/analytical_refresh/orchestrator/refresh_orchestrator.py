import uuid
from datetime import datetime, timezone
from power_bi_integration.exporters.model_exporter import PowerBIModelExporter
from analytical_refresh.validators.pre_refresh_validator import PreRefreshValidator
from analytical_refresh.contracts.refresh_contract import RefreshTelemetryRecord

class AnalyticalRefreshOrchestrator:
    """
    Orchestrates Phase 22 model export, runs pre-refresh validation gates,
    and publishes telemetry logging for Power BI consumption.
    """
    def __init__(self):
        self.exporter = PowerBIModelExporter()
        self.validator = PreRefreshValidator()

    def execute_refresh(self) -> RefreshTelemetryRecord:
        run_id = str(uuid.uuid4())[:8]
        start_time = datetime.now(timezone.utc)
        
        telemetry = RefreshTelemetryRecord(
            run_id=run_id,
            start_time=start_time
        )

        try:
            # Step 1: Generate Phase 22 analytical models
            exported_files = self.exporter.export_models()
            telemetry.feeds_refreshed = list(exported_files.keys())

            # Step 2: Run Pre-Refresh Validation Gate
            validation_report = self.validator.validate_feeds()
            
            feed_validation_passed = True
            for feed, details in validation_report["feed_details"].items():
                telemetry.validation_results[feed] = details["valid"]
                telemetry.record_counts[feed] = details["count"]
                if not details["valid"]:
                    feed_validation_passed = False

            # Step 3: Determine Status
            if validation_report["overall_valid"] and feed_validation_passed:
                telemetry.overall_status = "PASS"
            else:
                telemetry.overall_status = "FAIL"
                telemetry.failure_reason = "Pre-refresh validation failed schema or record completeness checks."

        except Exception as e:
            telemetry.overall_status = "BLOCKED"
            telemetry.failure_reason = f"Exception during refresh pipeline execution: {str(e)}"

        telemetry.end_time = datetime.now(timezone.utc)
        return telemetry
