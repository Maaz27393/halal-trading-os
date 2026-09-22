import unittest
from investigation_reporting.analysis.analyzer import InvestigationAnalyzer
from investigation_reporting.reporting.generator import ReportGenerator
from investigation_reporting.audit.logger import InvestigationAuditLogger

class TestInvestigationReporting(unittest.TestCase):
    def test_investigation_pipeline(self):
        analyzer = InvestigationAnalyzer()
        report = analyzer.analyze(trigger="scheduled_routine_audit")

        self.assertIsNotNone(report.investigation_id)
        self.assertEqual(report.trigger, "scheduled_routine_audit")
        self.assertGreater(len(report.evidence), 0)
        self.assertGreater(len(report.observed_facts), 0)
        self.assertGreater(len(report.derived_findings), 0)

        generator = ReportGenerator(report)
        json_output = generator.to_json()
        markdown_output = generator.to_markdown()

        self.assertIn(report.investigation_id, json_output)
        self.assertIn("Automated Investigation Report", markdown_output)

        logger = InvestigationAuditLogger()
        audit_rec = logger.record_audit(report.investigation_id, report.trigger, "COMPLETED")
        self.assertEqual(audit_rec["status"], "COMPLETED")

        print("\n--- PHASE 28 INVESTIGATION REPORT SUMMARY ---")
        print(markdown_output)
        print("-----------------------------------------------\n")

if __name__ == "__main__":
    unittest.main()
