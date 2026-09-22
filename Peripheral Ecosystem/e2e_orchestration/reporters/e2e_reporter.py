from e2e_orchestration.contracts.e2e_contract import E2ERunResult

class E2EReporter:
    """
    Generates canonical JSON and Markdown reports for E2E orchestration runs.
    """
    def __init__(self, result: E2ERunResult):
        self.result = result

    def to_json(self) -> str:
        return self.result.model_dump_json(indent=2)

    def to_markdown(self) -> str:
        r = self.result
        md = []
        md.append(f"# Ecosystem End-to-End Orchestration Report: `{r.run_id}`")
        md.append(f"**Started At:** `{r.started_at.isoformat()}` | **Completed At:** `{r.completed_at.isoformat() if r.completed_at else 'N/A'}`")
        md.append(f"**Overall Status:** `{r.overall_status}` | **Certification Gate:** `{r.certification_gate}`\n")

        md.append("## 1. Phase Results (Phases 20–29)")
        for p in r.phase_results:
            md.append(f"- **Phase {p.phase_number} ({p.phase_name}):** `{p.status}`")

        md.append("\n## 2. Cross-Phase Contract Validation")
        for cp in r.cross_phase_results:
            md.append(f"- **Phase {cp.source_phase} → Phase {cp.target_phase} ({cp.contract_name}):** `{cp.status}` — {cp.notes}")

        if r.failure_injections:
            md.append("\n## 3. Failure Injections")
            for fi in r.failure_injections:
                md.append(f"- **{fi.injection_type} on {fi.target_domain}:** `{fi.status}` — {fi.observed_behavior}")

        md.append("\n## 4. Governance & Safety Invariants")
        for k, v in r.governance_state.items():
            md.append(f"- **{k}**: `{v}`")

        return "\n".join(md)
