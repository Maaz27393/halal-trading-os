import unittest
from ecosystem_certification.certification.certifier import EcosystemCertifier

class TestEcosystemCertification(unittest.TestCase):
    def test_ecosystem_certification_pipeline(self):
        certifier = EcosystemCertifier()
        result = certifier.run_certification()

        self.assertEqual(result.overall_status, "CERTIFIED")
        self.assertTrue(result.epistemic_integrity)
        self.assertTrue(result.governance_integrity)
        self.assertEqual(len(result.subsystem_statuses), 10)

        print("\n--- PHASE 39 UNIFIED ECOSYSTEM CERTIFICATION REPORT ---")
        print(f"Certification ID: {result.certification_id} | Overall Status: {result.overall_status}")
        print("Subsystem Validation Summary:")
        for sub, status in result.subsystem_statuses.items():
            print(f"  - {sub}: {status}")
        print(f"Epistemic Integrity: {result.epistemic_integrity} | Governance Integrity: {result.governance_integrity}")
        print(f"Security Boundary: Read-Only = {result.security_boundary['read_only']} | Execution Authority = {result.security_boundary['execution_authority']}")
        print("-------------------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
