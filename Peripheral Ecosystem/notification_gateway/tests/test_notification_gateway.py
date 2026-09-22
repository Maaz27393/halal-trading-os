import unittest
import uuid
from notification_gateway.contracts.alert_contract import AlertEvent
from notification_gateway.policies.policy_engine import AlertPolicyEngine
from notification_gateway.delivery.reliability import DeliveryTelemetryManager

class TestNotificationGateway(unittest.TestCase):
    def test_notification_pipeline(self):
        policy_engine = AlertPolicyEngine()
        policy = policy_engine.evaluate_policy("WARNING")
        
        alert_id = str(uuid.uuid4())[:8]
        alert = AlertEvent(
            alert_id=alert_id,
            investigation_id="inv-48711f85",
            severity="WARNING",
            event_type="PROVIDER_DEGRADATION_WARNING",
            summary="System health warning detected during automated audit.",
            report_reference="Peripheral Ecosystem/investigation_reporting/reports/inv-48711f85.json",
            provenance="Phase28InvestigationEngine",
            delivery_policy=policy
        )

        manager = DeliveryTelemetryManager()
        telemetry = manager.process_alert(alert)

        self.assertEqual(telemetry["alert_id"], alert_id)
        self.assertIn("local_drop", telemetry["lifecycle_results"])
        self.assertIn("webhook", telemetry["lifecycle_results"])
        self.assertEqual(telemetry["lifecycle_results"]["local_drop"]["status"], "SUCCESS")
        self.assertEqual(telemetry["lifecycle_results"]["webhook"]["status"], "SUCCESS")

        # Test Duplicate Suppression
        dup_telemetry = manager.process_alert(alert)
        self.assertEqual(dup_telemetry["status"], "DUPLICATE_SUPPRESSED")

        print("\n--- PHASE 29 NOTIFICATION GATEWAY REPORT ---")
        print(f"Alert ID: {alert.alert_id}")
        print(f"Severity: {alert.severity} | Policy Action: {policy['action']}")
        print(f"Delivery Results: {telemetry['lifecycle_results']}")
        print(f"Security Boundary Verified: {alert.security_boundary}")
        print("-----------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
