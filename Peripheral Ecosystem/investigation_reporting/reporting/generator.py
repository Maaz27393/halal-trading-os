from investigation_reporting.contracts.investigation_contract import InvestigationReport

class ReportGenerator:
    """
    Generates canonical JSON and human-readable Markdown reports from investigation results.
    """
    def __init__(self, report: InvestigationReport):
        self.report = report

    def to_json(self) -> str:
        return self.report.model_dump_json(indent=2)

    def to_markdown(self) -> str:
        r = self.report
        md = []
        md.append(f"# Automated Investigation Report: `{r.investigation_id}`")
        md.append(f"**Trigger:** {r.trigger} | **Timestamp:** {r.report_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        md.append(f"**System Status:** `{r.system_status}` | **Regression:** `{r.regression_status}` | **Data Quality:** `{r.data_quality_status}`\n")
        
        md.append("## 1. Affected Domains")
        for dom in r.affected_domains:
            md.append(f"- {dom}")
        
        md.append("\n## 2. Observed Facts")
        for f in r.observed_facts:
            md.append(f"- {f}")

        md.append("\n## 3. Derived Findings")
        for d in r.derived_findings:
            md.append(f"- {d}")

        md.append("\n## 4. Unresolved Questions")
        for q in r.unresolved_questions:
            md.append(f"- {q}")

        md.append("\n## 5. Safety & Governance Invariants")
        for k, v in r.safety_governance.items():
            md.append(f"- **{k}**: `{v}`")

        return "\n".join(md)
