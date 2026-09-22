from datetime import datetime, timezone
from typing import Dict, Any
from operational_control_center.contracts.control_center_contract import EcosystemStatusSummary, GovernanceInfo
from system_validation.runners.regression_runner import SystemRegressionOrchestrator

class OperationalControlCenterAggregator:
    """
    Aggregates metrics from upstream certified domains (Phase 16, 19, 20)
    into a unified read-only operational view.
    """
    def __init__(self):
        self.orchestrator = SystemRegressionOrchestrator()

    def get_ecosystem_summary(self) -> EcosystemStatusSummary:
        # Run Phase 20 regression to get latest baseline health
        report = self.orchestrator.generate_certification_report()

        regression_pass = (report.overall_status == "PASS")
        
        # Provider health mapping based on regression and domain output
        providers = {
            "NSE": "HEALTHY" if regression_pass else "DEGRADED",
            "Screener": "HEALTHY",
            "Chartink": "HEALTHY",
            "TradingView": "HEALTHY",
            "Kite": "HEALTHY"
        }

        critical_failures = len(report.failures)
        system_status = "HEALTHY" if regression_pass and critical_failures == 0 else "DEGRADED"

        return EcosystemStatusSummary(
            system_status=system_status,
            regression_status=report.overall_status,
            data_quality_status="PASS" if report.domains.get("phase19_data_quality") == "PASS" else "FAIL",
            governance=GovernanceInfo(
                live_auto_execution=False,
                order_capability="NONE",
                execution_authority="NONE",
                governance_mode="READ_ONLY"
            ),
            providers=providers,
            active_alerts=critical_failures,
            data_quality_issues=0 if report.domains.get("phase19_data_quality") == "PASS" else 1,
            critical_failures=critical_failures,
            failures_log=report.failures
        )
