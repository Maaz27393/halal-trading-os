import unittest
from session_management.managers.session_manager import SessionManager
from session_management.contracts.session_contract import SessionState
from session_management.health.central_health_aggregator import CentralHealthAggregator

class TestSessionManagement(unittest.TestCase):
    def test_session_lifecycle_and_fail_closed(self):
        sm = SessionManager()
        meta = sm.register_provider("test_provider", SessionState.VALID)
        self.assertEqual(meta.session_state, SessionState.VALID)
        self.assertTrue(meta.authenticated)

        # First failure -> DEGRADED
        meta_deg = sm.update_session_status("test_provider", success=False, failure_reason="Timeout")
        self.assertEqual(meta_deg.session_state, SessionState.DEGRADED)

        # Second failure -> EXPIRED
        meta_exp = sm.update_session_status("test_provider", success=False, failure_reason="Still down")
        self.assertEqual(meta_exp.session_state, SessionState.EXPIRED)

        # Third failure -> REAUTH_REQUIRED
        meta_reauth = sm.update_session_status("test_provider", success=False, failure_reason="Auth revoked")
        self.assertEqual(meta_reauth.session_state, SessionState.REAUTH_REQUIRED)
        self.assertTrue(meta_reauth.reauth_required)

    def test_aggregator_initialization(self):
        sm = SessionManager()
        aggregator = CentralHealthAggregator(sm)
        report = aggregator.refresh_all_health()
        self.assertIn("providers", report)
        self.assertIn("nse_provider", report["providers"])
        self.assertIn("kite_provider", report["providers"])

if __name__ == "__main__":
    unittest.main()
