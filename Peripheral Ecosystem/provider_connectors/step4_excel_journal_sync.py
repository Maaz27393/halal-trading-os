import os
import csv
import logging
from typing import List, Dict, Any
from pydantic import BaseModel

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from provider_connectors.step3_kite_readonly import TradeJournalRecord

logger = logging.getLogger("ProviderStep4_ExcelJournalSync")

class ExcelJournalSyncConnector:
    """
    Provider Integration Step 4:
    Automates the synchronization of read-only tradebook data into your local Excel / CSV 
    trading journal for seamless Power BI analytics consumption.
    Enforces strict PermissionGateway checks and LIVE_AUTO_EXECUTION = FALSE.
    """

    def __init__(self, permission_gateway: PermissionGateway, role: str = "analyst_agent"):
        self.permission_gateway = permission_gateway
        self._connected = False
        self._role = role
        self.journal_path = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem\\Canonical Universe\\Trading_Journal.csv"
        logger.info("ExcelJournalSyncConnector initialized.")

    def connect(self) -> bool:
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")
        
        if not self.permission_gateway.verify_permission(self._role, "WRITE"):
            raise PermissionError(f"Role '{self._role}' lacks write/sync permissions for journal logging.")

        self._connected = True
        logger.info("Connected successfully to Excel Journal Sync pipeline.")
        return True

    def sync_trades_to_journal(self, trades: List[TradeJournalRecord]) -> str:
        """
        Appends new executed trades into the canonical Trading Journal CSV 
        for Power BI live refresh.
        """
        if not self._connected:
            raise ConnectionError("ExcelJournalSyncConnector is not connected.")

        if not self.permission_gateway.verify_permission(self._role, "WRITE"):
            raise PermissionError("Permission denied for writing journal entries.")

        os.makedirs(os.path.dirname(self.journal_path), exist_ok=True)
        
        file_exists = os.path.exists(self.journal_path)
        headers = ["trade_id", "symbol", "transaction_type", "quantity", "average_price", "order_timestamp", "has_execution_payload"]

        written_count = 0
        existing_trade_ids = set()

        if file_exists:
            with open(self.journal_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "trade_id" in row:
                        existing_trade_ids.add(row["trade_id"])

        with open(self.journal_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()

            for t in trades:
                if t.trade_id not in existing_trade_ids:
                    writer.writerow({
                        "trade_id": t.trade_id,
                        "symbol": t.symbol,
                        "transaction_type": t.transaction_type,
                        "quantity": t.quantity,
                        "average_price": t.average_price,
                        "order_timestamp": t.order_timestamp,
                        "has_execution_payload": str(t.has_execution_payload)
                    })
                    written_count += 1

        logger.info(f"Successfully synchronized {written_count} new trade(s) to journal: {self.journal_path}")
        return self.journal_path

    def disconnect(self) -> bool:
        self._connected = False
        logger.info("Disconnected from Excel Journal Sync pipeline.")
        return True