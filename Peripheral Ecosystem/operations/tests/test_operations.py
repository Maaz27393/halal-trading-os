import unittest
from operations.contracts.operational_contract import OperationalEvent
from operations.telemetry.observability import SystemObservabilityAggregator
from operations.recovery.disaster_recovery import DisasterRecoveryEngine

class TestPhase16Operations(unittest.TestCase):
    def test_observability_and_governance(self):
        aggregator = SystemObservabilityAggregator()
        self.assertFalse(aggregator.live_auto_execution)

        aggregator.record_domain_status("session_management", "HEALTHY")
        aggregator.record_domain_status("backtesting", "HEALTHY")
        
        summary = aggregator.get_system_health_summary()
        self.assertEqual(summary["overall_status"], "HEALTHY")
        self.assertFalse(summary["live_auto_execution"])

    def test_disaster_recovery_containment(self):
        recovery = DisasterRecoveryEngine()
        result = recovery.handle_failure("nse_provider", 403, "Forbidden / Token Expired")
        
        self.assertEqual(result["containment_action"], "REAUTH_REQUIRED")
        self.assertEqual(result["system_state"], "SAFE_LOCKED")
        self.assertFalse(result["live_auto_execution"])

if __name__ == "__main__":
    unittest.main()
