import uuid
from typing import List
from investigation_reporting.contracts.investigation_contract import InvestigationReport, EvidenceItem
from investigation_reporting.evidence.collector import EvidenceCollector

class InvestigationAnalyzer:
    """
    Analyzes collected evidence, strictly distinguishing observed facts,
    derived findings, and unresolved questions without fabricating data.
    """
    def __init__(self):
        self.collector = EvidenceCollector()

    def analyze(self, trigger: str) -> InvestigationReport:
        investigation_id = str(uuid.uuid4())[:8]
        evidence_items = self.collector.collect_evidence()

        affected_domains = list(set([e.source_domain for e in evidence_items]))
        
        observed_facts = []
        derived_findings = []
        unresolved_questions = []

        sys_status = "UNKNOWN"
        reg_status = "UNKNOWN"
        dq_status = "UNKNOWN"

        for ev in evidence_items:
            observed_facts.append(f"[{ev.source_domain}] {ev.content}")
            
            if ev.source_domain == "CONTROL_CENTER":
                meta = ev.raw_metadata
                sys_status = meta.get("system_status", "UNKNOWN")
                reg_status = meta.get("regression_status", "UNKNOWN")
                dq_status = meta.get("data_quality_status", "UNKNOWN")
                if meta.get("critical_failures", 0) > 0:
                    derived_findings.append("Critical failures detected in control center telemetry.")
                else:
                    derived_findings.append("Control center reports zero critical failures across monitored providers.")
            elif ev.source_domain == "REGRESSION":
                if ev.raw_metadata.get("overall_status") == "PASS":
                    derived_findings.append("System regression certification suite passed successfully.")
                else:
                    derived_findings.append("System regression certification suite reported failures or warnings.")

        if not observed_facts:
            unresolved_questions.append("No verified evidence items were returned during collection.")
        else:
            unresolved_questions.append("Are there any secondary intermittent provider latencies not captured in current snapshot?")

        return InvestigationReport(
            investigation_id=investigation_id,
            trigger=trigger,
            affected_domains=affected_domains,
            evidence=evidence_items,
            observed_facts=observed_facts,
            derived_findings=derived_findings,
            unresolved_questions=unresolved_questions,
            data_quality_status=dq_status,
            system_status=sys_status,
            regression_status=reg_status
        )
