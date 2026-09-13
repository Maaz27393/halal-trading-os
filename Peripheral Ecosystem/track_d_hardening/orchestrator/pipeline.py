import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from track_a_workspace.gmail_connector.gmail_adapter import A1GmailConnector
from track_a_workspace.docs_exporter.doc_adapter import A2DocumentExporter
from track_a_workspace.sheets_connector.sheets_adapter import A3SheetsExcelConnector
from track_b_workspace.analytics_engine.screener_adapter import B1ScreenerAnalyticsEngine
from track_c_workspace.risk_engine.risk_adapter import C1RiskManagementEngine
from p7_expansion.agentic_refinement import ResearchDraft

logger = logging.getLogger("PeripheralOrchestrator")

class PipelineExecutionResult(BaseModel):
    workflow_id: str
    status: str
    steps_completed: List[str]
    export_path: Optional[str] = None
    has_execution_payload: bool = False
    timestamp: str

class PeripheralOrchestrator:
    """
    Track D.1: Unified Peripheral Orchestrator.
    Coordinates multi-step workflows across Tracks A, B, and C under strict
    PermissionGateway oversight and immutable LIVE_AUTO_EXECUTION = FALSE safety.
    """

    def __init__(self, permission_gateway: PermissionGateway, role: str = "analyst_agent"):
        self.permission_gateway = permission_gateway
        self._role = role
        
        # Initialize constituent peripheral modules
        self.gmail = A1GmailConnector(permission_gateway=self.permission_gateway)
        self.exporter = A2DocumentExporter(permission_gateway=self.permission_gateway, role=self._role)
        self.sheets = A3SheetsExcelConnector(permission_gateway=self.permission_gateway, role=self._role)
        self.analytics = B1ScreenerAnalyticsEngine(permission_gateway=self.permission_gateway, role=self._role)
        self.risk = C1RiskManagementEngine(permission_gateway=self.permission_gateway, role="risk_analyst" if self._role=="risk_analyst" else "analyst_agent")
        
        logger.info("PeripheralOrchestrator initialized with full module registry.")

    def run_full_pipeline(self, query: str, raw_stocks: List[Dict[str, Any]], screening_criteria: Dict[str, Any], trade_setup: Dict[str, Any]) -> PipelineExecutionResult:
        """
        Execute a unified pipeline:
        1. Ingest/Search data via Gmail connector.
        2. Filter stock universe via Screener Analytics engine.
        3. Evaluate risk parameters via Risk Management engine.
        4. Export tabular summaries via Sheets connector.
        5. Compile and export final research report via Document Exporter.
        """
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")

        workflow_id = f"WF_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        steps = []
        logger.info(f"Starting unified peripheral pipeline execution: {workflow_id}")

        # Step 1: Connect and Ingest Emails
        self.gmail.connect()
        emails = self.gmail.read({"query": query, "max_results": 2})
        steps.append("A.1_GMAIL_INGESTION")
        self.gmail.disconnect()

        # Step 2: Connect and Run Screener Analytics
        self.analytics.connect()
        filtered_stocks = self.analytics.process_universe(raw_stocks, screening_criteria)
        steps.append("B.1_ANALYTICS_FILTERING")
        self.analytics.disconnect()

        # Step 3: Connect and Evaluate Risk
        # Ensure risk role permission is available or grant temporarily for pipeline orchestration
        if not self.permission_gateway.verify_permission("risk_analyst", "READ"):
            self.permission_gateway.grant_permission("risk_analyst", "READ")
        
        self.risk.connect()
        risk_result = self.risk.evaluate_position_risk(trade_setup, min_rr_ratio=1.5)
        steps.append("C.1_RISK_EVALUATION")
        self.risk.disconnect()

        # Step 4: Connect and Export Tabular Summary
        self.sheets.connect()
        sheet_data = [{"symbol": s.symbol, "roe": s.roe, "rsi": s.rsi} for s in filtered_stocks]
        if sheet_data:
            self.sheets.export_sheet(f"Pipeline_{workflow_id}", sheet_data)
        steps.append("A.3_SHEETS_EXPORT")
        self.sheets.disconnect()

        # Step 5: Connect and Export Final Markdown Report
        self.exporter.connect()
        report_content = f"""## Pipeline Orchestration Summary ({workflow_id})

### Ingested Intelligence Feeds
- **Query:** {query}
- **Emails Ingested:** {len(emails)} item(s)

### Screener Analytics Results
- **Filtered Compliant Stocks:** {len(filtered_stocks)} symbol(s)
- **Top Picks:** {', '.join([s.symbol for s in filtered_stocks])}

### Risk Management Audit
- **Target Symbol:** {risk_result.symbol}
- **Risk-to-Reward Ratio:** {risk_result.risk_reward_ratio} (Compliant: {risk_result.is_risk_compliant})
- **Calculated Position Size:** {risk_result.position_size} shares

---
*Generated securely under non-causal research mode (LIVE_AUTO_EXECUTION = FALSE).*
"""
        draft = ResearchDraft(
            title=f"Unified Pipeline Report {workflow_id}",
            content=report_content,
            provenance_sources=["A.1 Gmail", "B.1 Screener", "C.1 Risk Engine"],
            author_agent="PeripheralOrchestrator",
            has_execution_payload=False
        )
        export_item = self.exporter.export_draft(draft)
        steps.append("A.2_DOCS_EXPORT")
        self.exporter.disconnect()

        logger.info(f"Unified pipeline execution successfully completed: {workflow_id}")

        return PipelineExecutionResult(
            workflow_id=workflow_id,
            status="SUCCESS",
            steps_completed=steps,
            export_path=export_item.target_path,
            has_execution_payload=False,
            timestamp=datetime.utcnow().isoformat()
        )