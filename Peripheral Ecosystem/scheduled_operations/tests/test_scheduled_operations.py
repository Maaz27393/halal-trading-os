import unittest
from scheduled_operations.scheduler.refresh_scheduler import ScheduledOperationsEngine

class TestScheduledOperations(unittest.TestCase):
    def test_scheduled_job_lifecycle(self):
        engine = ScheduledOperationsEngine()
        telemetry = engine.run_job(trigger_type="MANUAL")

        self.assertEqual(telemetry.lifecycle_status, "COMPLETED")
        self.assertEqual(telemetry.overall_status, "PASS")
        self.assertTrue(telemetry.publication_result)
        self.assertFalse(telemetry.safeguards["live_auto_execution"])
        self.assertEqual(telemetry.safeguards["order_capability"], "NONE")

        print("\n--- PHASE 24 SCHEDULED LIFECYCLE TELEMETRY ---")
        print(f"Run ID: {telemetry.run_id}")
        print(f"Trigger Type: {telemetry.trigger_type}")
        print(f"Lifecycle Status: {telemetry.lifecycle_status}")
        print(f"Overall Status: {telemetry.overall_status}")
        print(f"Publication Result: {telemetry.publication_result}")
        print(f"Duration: {telemetry.duration_seconds:.4f}s")
        print(f"Safeguards: {telemetry.safeguards}")
        print("----------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
