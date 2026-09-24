import unittest
from production_hardening.acceptance.hardening_manager import ProductionHardeningManager

class TestProductionHardening(unittest.TestCase):
    def test_production_hardening_pipeline(self):
        manager = ProductionHardeningManager()
        result = manager.run_acceptance()

        self.assertEqual(result.acceptance_status, "ACCEPTED")
        self.assertTrue(result.security_audit_passed)
        self.assertEqual(len(result.hardening_checks), 5)

        print("\n--- PHASE 40 PRODUCTION ACCEPTANCE REPORT ---")
        print(f"Acceptance ID: {result.acceptance_id} | Final Gate Status: {result.acceptance_status}")
        print("Hardening Checks Summary:")
        for check, status in result.hardening_checks.items():
            print(f"  - {check}: {status}")
        print("Operational Baseline Summary:")
        for k, v in result.baseline_summary.items():
            print(f"  - {k}: {v}")
        print(f"Security Boundary: Read-Only = {result.security_boundary['read_only']} | Execution Authority = {result.security_boundary['execution_authority']}")
        print(f"Operational Runbook: Initialized & Verified at Peripheral Ecosystem/production_hardening/runbooks/OPERATIONAL_RUNBOOK.md")
        print("----------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
