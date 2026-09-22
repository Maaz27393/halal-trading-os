import unittest
import sys
import os
import uuid
import json
import contextlib
from datetime import datetime, timezone
from system_validation.contracts.report_contract import CertificationReport, GovernanceState

class SystemRegressionOrchestrator:
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.failures = []
        self.domain_results = {}

    def run_suite(self, module_name: str, domain_label: str) -> bool:
        try:
            __import__(module_name)
            suite = unittest.defaultTestLoader.loadTestsFromName(module_name)
            
            # Suppress standard output during automated test run using context manager
            with open(os.devnull, 'w') as devnull, contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                runner = unittest.TextTestRunner(stream=devnull, verbosity=0)
                result = runner.run(suite)
            
            if result.wasSuccessful():
                self.domain_results[domain_label] = "PASS"
                return True
            else:
                self.domain_results[domain_label] = "FAIL"
                for failure in result.failures:
                    self.failures.append(f"[{domain_label}] FAIL: {failure[0]} - {failure[1][:100]}")
                for error in result.errors:
                    self.failures.append(f"[{domain_label}] ERROR: {error[0]} - {error[1][:100]}")
                return False
        except Exception as e:
            self.domain_results[domain_label] = "BLOCKED"
            self.failures.append(f"[{domain_label}] BLOCKED: Exception during test load/execution: {str(e)}")
            return False

    def generate_certification_report(self) -> CertificationReport:
        self.run_suite("operations.tests.test_operations", "phase16_operations")
        self.run_suite("data_quality.tests.test_quality_gate", "phase19_data_quality")
        self.run_suite("assurance.assurance_runner", "phase17_assurance")

        overall = "PASS" if all(status == "PASS" for status in self.domain_results.values()) else "FAIL"
        if any(status == "BLOCKED" for status in self.domain_results.values()):
            overall = "BLOCKED"

        report = CertificationReport(
            run_id=self.run_id,
            overall_status=overall,
            domains=self.domain_results,
            governance=GovernanceState(live_auto_execution=False, order_capability="NONE", execution_authority="NONE"),
            failures=self.failures
        )
        return report
