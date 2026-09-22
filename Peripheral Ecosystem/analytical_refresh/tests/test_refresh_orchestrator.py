import unittest
from analytical_refresh.orchestrator.refresh_orchestrator import AnalyticalRefreshOrchestrator

class TestAnalyticalRefreshOrchestrator(unittest.TestCase):
    def test_refresh_execution(self):
        orchestrator = AnalyticalRefreshOrchestrator()
        telemetry = orchestrator.execute_refresh()

        self.assertIsNotNone(telemetry.run_id)
        self.assertEqual(telemetry.overall_status, "PASS")
        self.assertGreater(len(telemetry.feeds_refreshed), 0)
        
        print("\n--- PHASE 23 REFRESH TELEMETRY REPORT ---")
        print(f"Run ID: {telemetry.run_id}")
        print(f"Status: {telemetry.overall_status}")
        print(f"Feeds Refreshed: {telemetry.feeds_refreshed}")
        print(f"Record Counts: {telemetry.record_counts}")
        print(f"Validation Results: {telemetry.validation_results}")
        print(f"Start Time: {telemetry.start_time}")
        print(f"End Time: {telemetry.end_time}")
        print("------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
