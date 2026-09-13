import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("A3SheetsExcelConnector")

class TabularDataRow(BaseModel):
    row_id: str
    data: Dict[str, Any]
    tags: List[str] = Field(default_factory=list)
    has_execution_payload: bool = False

class A3SheetsExcelConnector:
    """
    Track A.3: Secure Google Sheets / Excel Connector.
    Handles tabular data ingestion and export for risk models and backtest summaries.
    Enforces strict permission gating via PermissionGateway.
    Maintains zero execution authority.
    """

    def __init__(self, permission_gateway: PermissionGateway, role: str = "analyst_agent", data_root: Optional[str] = None):
        self.permission_gateway = permission_gateway
        self._connected = False
        self._role = role
        self.data_root = data_root or "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem\\Tabular Data"
        logger.info("A3SheetsExcelConnector initialized with secure tabular boundary.")

    def connect(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """Establish secure boundary connection for tabular operations."""
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")
        
        if not self.permission_gateway.verify_permission(self._role, "READ") and not self.permission_gateway.verify_permission(self._role, "WRITE"):
            logger.error(f"Tabular connection denied: Role '{self._role}' lacks necessary permissions.")
            raise PermissionError(f"Role '{self._role}' lacks tabular read/write permissions.")

        self._connected = True
        logger.info("A3SheetsExcelConnector successfully connected (Tabular Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        """Return connector health status."""
        return {
            "status": "HEALTHY" if self._connected else "DISCONNECTED",
            "connector": "A3SheetsExcelConnector",
            "live_auto_execution": LIVE_AUTO_EXECUTION,
            "permissions": "TABULAR READ/WRITE"
        }

    def capabilities(self) -> List[str]:
        """Declare strict tabular data capabilities."""
        return [
            "read_tabular_dataset",
            "export_tabular_dataset",
            "normalize_table_to_research",
            "validate_risk_matrix"
        ]

    def read_sheet(self, sheet_identifier: str) -> List[TabularDataRow]:
        """
        Read structured tabular data from sheets/spreadsheets.
        Enforces strict READ permission gating.
        """
        if not self._connected:
            raise ConnectionError("A3SheetsExcelConnector is not connected.")

        if not self.permission_gateway.verify_permission(self._role, "READ"):
            raise PermissionError(f"Permission DENIED for role '{self._role}' on operation 'READ'.")

        logger.info(f"Reading tabular dataset from identifier: '{sheet_identifier}'")

        # Mock structured risk/backtest data rows for analytical ingestion
        mock_rows = [
            TabularDataRow(
                row_id="row_001",
                data={"symbol": "NIFTY_50", "strategy": "EMA_Pullback", "win_rate": 0.62, "sharpe_ratio": 1.45, "max_drawdown": -0.045},
                tags=["Backtest", "Performance"],
                has_execution_payload=False
            ),
            TabularDataRow(
                row_id="row_002",
                data={"symbol": "BANKNIFTY", "strategy": "VWAP_Reversion", "win_rate": 0.58, "sharpe_ratio": 1.28, "max_drawdown": -0.062},
                tags=["Backtest", "Performance"],
                has_execution_payload=False
            )
        ]
        return mock_rows

    def export_sheet(self, dataset_name: str, rows: List[Dict[str, Any]]) -> str:
        """
        Export tabular rows into a structured CSV file within the vault.
        Enforces strict WRITE permission gating.
        """
        if not self._connected:
            raise ConnectionError("A3SheetsExcelConnector is not connected.")

        if not self.permission_gateway.verify_permission(self._role, "WRITE"):
            raise PermissionError(f"Permission DENIED for role '{self._role}' on operation 'WRITE'.")

        os.makedirs(self.data_root, exist_ok=True)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = f"SheetExport_{date_str}_{dataset_name}.csv"
        target_path = os.path.join(self.data_root, filename)

        if not rows:
            raise ValueError("Export dataset contains zero rows.")

        headers = list(rows[0].keys())
        csv_lines = [",".join(headers)]
        for r in rows:
            csv_lines.append(",".join([str(r.get(h, "")) for h in headers]))

        with open(target_path, "w", encoding="utf-8") as f:
            f.write("\n".join(csv_lines))

        logger.info(f"Successfully exported tabular dataset to: {target_path}")
        return target_path

    def disconnect(self) -> bool:
        """Disconnect and clear session boundary."""
        self._connected = False
        logger.info("A3SheetsExcelConnector disconnected.")
        return True