import json
import os
from datetime import datetime, timezone
from operational_control_center.aggregators.control_center_aggregator import OperationalControlCenterAggregator

class PowerBIModelExporter:
    """
    Transforms Phase 21 control center summaries into structured, flat/star-schema
    datasets ready for Power BI consumption.
    """
    def __init__(self, output_dir: str = "Peripheral Ecosystem/power_bi_integration/models"):
        self.aggregator = OperationalControlCenterAggregator()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_models(self) -> dict:
        summary = self.aggregator.get_ecosystem_summary()
        timestamp_str = summary.timestamp.isoformat()

        # 1. Dimension Table: Providers
        providers_data = [
            {"provider_name": name, "status": status, "snapshot_timestamp": timestamp_str}
            for name, status in summary.providers.items()
        ]

        # 2. Fact Table: System Health & Regression
        system_health_data = [{
            "run_id": summary.timestamp.strftime("%Y%m%d%H%M%S"),
            "timestamp": timestamp_str,
            "system_status": summary.system_status,
            "regression_status": summary.regression_status,
            "data_quality_status": summary.data_quality_status,
            "active_alerts": summary.active_alerts,
            "data_quality_issues": summary.data_quality_issues,
            "critical_failures": summary.critical_failures
        }]

        # 3. Dimension Table: Governance State
        governance_data = [{
            "governance_mode": summary.governance.governance_mode,
            "live_auto_execution": summary.governance.live_auto_execution,
            "order_capability": summary.governance.order_capability,
            "execution_authority": summary.governance.execution_authority,
            "snapshot_timestamp": timestamp_str
        }]

        # Write out to JSON/CSV mock files for Power BI ingestion
        exported_files = {}
        
        prov_path = os.path.join(self.output_dir, "dim_providers.json")
        with open(prov_path, "w", encoding="utf-8") as f:
            json.dump(providers_data, f, indent=2)
        exported_files["dim_providers"] = prov_path

        health_path = os.path.join(self.output_dir, "fact_system_health.json")
        with open(health_path, "w", encoding="utf-8") as f:
            json.dump(system_health_data, f, indent=2)
        exported_files["fact_system_health"] = health_path

        gov_path = os.path.join(self.output_dir, "dim_governance.json")
        with open(gov_path, "w", encoding="utf-8") as f:
            json.dump(governance_data, f, indent=2)
        exported_files["dim_governance"] = gov_path

        return exported_files
