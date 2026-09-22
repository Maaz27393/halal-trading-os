import unittest
import json
from system_validation.runners.regression_runner import SystemRegressionOrchestrator

class TestSystemValidationRunner(unittest.TestCase):
    def test_orchestrator_execution(self):
        orchestrator = SystemRegressionOrchestrator()
        report = orchestrator.generate_certification_report()
        
        self.assertIsNotNone(report.run_id)
        self.assertIn(report.overall_status, ["PASS", "FAIL", "BLOCKED"])
        self.assertFalse(report.governance.live_auto_execution)
        
        print("\n--- SYSTEM CERTIFICATION JSON REPORT ---")
        # Use model_dump() for Pydantic V2 compliance
        dump_data = report.model_dump() if hasattr(report, "model_dump") else report.dict()
        print(json.dumps(dump_data, default=str, indent=2))
        print("------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
