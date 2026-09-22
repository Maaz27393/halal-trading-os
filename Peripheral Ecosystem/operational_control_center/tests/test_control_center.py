import unittest
import json
from operational_control_center.aggregators.control_center_aggregator import OperationalControlCenterAggregator

class TestOperationalControlCenter(unittest.TestCase):
    def test_aggregator_summary(self):
        aggregator = OperationalControlCenterAggregator()
        summary = aggregator.get_ecosystem_summary()

        self.assertIsNotNone(summary.system_status)
        self.assertIn(summary.regression_status, ["PASS", "FAIL", "BLOCKED"])
        self.assertFalse(summary.governance.live_auto_execution)
        self.assertEqual(summary.governance.order_capability, "NONE")
        self.assertEqual(summary.governance.execution_authority, "NONE")
        
        # Pretty print formatted human/machine output
        print("\n--- OPERATIONAL CONTROL CENTER STATUS ---")
        print(f"SYSTEM STATUS: {summary.system_status}")
        print(f"Regression: {summary.regression_status}")
        print(f"Data Quality: {summary.data_quality_status}")
        print(f"Governance Mode: {summary.governance.governance_mode}")
        print(f"Auto Execution: {str(summary.governance.live_auto_execution).upper()}")
        print(f"Execution Authority: {summary.governance.execution_authority}")
        print("\nProviders:")
        for prov, status in summary.providers.items():
            print(f"  {prov}: {status}")
        print(f"\nActive Alerts: {summary.active_alerts}")
        print(f"Data Quality Issues: {summary.data_quality_issues}")
        print(f"Critical Failures: {summary.critical_failures}")
        print("------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
