from interactive_dashboard.adapters.dashboard_adapter import DashboardAdapter

class InteractiveOperationsDashboard:
    """
    Renders the human-facing operational control room view.
    """
    def __init__(self):
        self.adapter = DashboardAdapter()

    def render_control_room(self) -> str:
        state = self.adapter.fetch_dashboard_state()

        output = []
        output.append("\n========================================================")
        output.append("   HALAL TRADING OS — INTERACTIVE OPERATIONS CONTROL ROOM")
        output.append("========================================================")
        output.append(f"Timestamp: {state.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')} | Mode: {state.safety_guarantee}")
        output.append("--------------------------------------------------------")
        
        # 1. System Overview
        output.append("[1] SYSTEM OVERVIEW")
        output.append(f"  • System Status    : {state.system_overview.get('system_status')}")
        output.append(f"  • Regression Status: {state.system_overview.get('regression_status')}")
        output.append(f"  • Data Quality     : {state.system_overview.get('data_quality_status')}")
        output.append(f"  • Critical Failures: {state.system_overview.get('critical_failures')}")

        # 2. Provider Health
        output.append("\n[2] PROVIDER HEALTH")
        for prov, health in state.provider_health.items():
            output.append(f"  • {prov:<12} : {health}")

        # 3. Data Quality
        output.append("\n[3] DATA QUALITY & FRESHNESS")
        output.append(f"  • Quality Status   : {state.data_quality.get('status')}")
        output.append(f"  • Ingestion State  : {state.data_quality.get('freshness')}")
        output.append(f"  • Completeness     : {state.data_quality.get('completeness')}")

        # 4. Governance Invariants
        output.append("\n[4] GOVERNANCE SAFEGUARDS")
        for k, v in state.governance.items():
            output.append(f"  • {k:<20} : {str(v).upper()}")

        # 5. Refresh Operations
        output.append("\n[5] REFRESH OPERATIONS")
        output.append(f"  • Last Run ID      : {state.refresh_operations.get('last_run_id')}")
        output.append(f"  • Lifecycle Status : {state.refresh_operations.get('lifecycle_status')}")
        output.append(f"  • Publication      : {state.refresh_operations.get('publication_result')}")
        output.append(f"  • Feeds Refreshed  : {state.refresh_operations.get('feeds_refreshed')}")

        # 6. Certification
        output.append("\n[6] SYSTEM CERTIFICATION (PHASE 20)")
        output.append(f"  • Overall Status   : {state.certification.get('overall_status')}")
        for dom, dstatus in state.certification.get('domains', {}).items():
            output.append(f"  • {dom:<22} : {dstatus}")

        # 7. Audit Trail
        output.append("\n[7] RECENT AUDIT TRAIL")
        for log in state.audit_trail[-3:]:
            output.append(f"  • [{log['timestamp'][11:19]}] {log['command']:<8} -> Status: {log['status']} (ID: {log['audit_id']})")

        output.append("========================================================\n")
        return "\n".join(output)
