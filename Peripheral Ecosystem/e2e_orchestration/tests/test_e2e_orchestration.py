import unittest
from e2e_orchestration.orchestrator.e2e_orchestrator import E2EOrchestrator
from e2e_orchestration.failure_injection.injector import FailureInjector
from e2e_orchestration.reporters.e2e_reporter import E2EReporter

class TestE2EOrchestration(unittest.TestCase):
    def test_e2e_pipeline(self):
        orchestrator = E2EOrchestrator()
        result = orchestrator.run_pipeline()

        injector = FailureInjector()
        fault_res = injector.inject_provider_degradation_failure()
        result.failure_injections.append(fault_res)

        reporter = E2EReporter(result)
        markdown_summary = reporter.to_markdown()

        self.assertEqual(result.overall_status, "PASS")
        self.assertEqual(result.certification_gate, "CERTIFIED")
        self.assertEqual(fault_res.status, "SAFE_CONTAINMENT")
        self.assertTrue(result.governance_state["read_only"])
        self.assertFalse(result.governance_state["live_auto_execution"])

        print("\n" + "="*50)
        print(markdown_summary)
        print("="*50 + "\n")

if __name__ == "__main__":
    unittest.main()
