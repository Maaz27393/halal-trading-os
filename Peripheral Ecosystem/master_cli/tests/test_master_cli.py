import unittest
from master_cli.cli.master_controller import MasterEcosystemController

class TestMasterEcosystemController(unittest.TestCase):
    def test_cli_commands(self):
        controller = MasterEcosystemController()

        # Test STATUS
        audit_status = controller.execute_command("STATUS")
        self.assertEqual(audit_status.command, "STATUS")
        self.assertEqual(audit_status.status, "PASS")

        # Test REFRESH
        audit_refresh = controller.execute_command("REFRESH")
        self.assertEqual(audit_refresh.command, "REFRESH")
        self.assertEqual(audit_refresh.status, "PASS")

        # Test CERTIFY
        audit_certify = controller.execute_command("CERTIFY")
        self.assertEqual(audit_certify.command, "CERTIFY")
        self.assertEqual(audit_certify.status, "PASS")

        # Test AUDIT
        audit_history_cmd = controller.execute_command("AUDIT")
        self.assertEqual(audit_history_cmd.command, "AUDIT")
        self.assertEqual(audit_history_cmd.status, "PASS")

        print("\n--- PHASE 25 MASTER CLI AUDIT REPORT ---")
        for log in [audit_status, audit_refresh, audit_certify, audit_history_cmd]:
            print(f"[{log.timestamp.strftime('%H:%M:%S')}] Command: {log.command} | Status: {log.status} | Audit ID: {log.audit_id}")
            print(f"  Details: {log.details}")
        print("------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
