import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("A1GmailConnector")

class GmailEmailItem(BaseModel):
    message_id: str
    sender: str
    subject: str
    timestamp: str
    body_snippet: str
    labels: List[str] = Field(default_factory=list)
    has_execution_payload: bool = False

class A1GmailConnector:
    """
    Track A.1: Secure, permission-gated Gmail Ingestion Connector.
    Enforces strict READ-ONLY and INGEST capabilities via PermissionGateway.
    Maintains zero execution authority.
    """

    def __init__(self, permission_gateway: PermissionGateway, role: str = "analyst_agent"):
        self.permission_gateway = permission_gateway
        self._connected = False
        self._role = role
        logger.info(f"A1GmailConnector initialized for role '{self._role}'.")

    def connect(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """Establish secure boundary connection with explicit permission verification."""
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")
        
        if not self.permission_gateway.verify_permission(self._role, "READ"):
            logger.error(f"Gmail connection denied: Role '{self._role}' lacks READ permission.")
            raise PermissionError(f"Role '{self._role}' lacks READ permission.")

        self._connected = True
        logger.info("A1GmailConnector successfully connected (Read-Only Mode).")
        return True

    def health(self) -> Dict[str, Any]:
        """Return connector health status."""
        return {
            "status": "HEALTHY" if self._connected else "DISCONNECTED",
            "connector": "A1GmailConnector",
            "live_auto_execution": LIVE_AUTO_EXECUTION,
            "permissions": "READ-ONLY"
        }

    def capabilities(self) -> List[str]:
        """Declare strict read/ingest capabilities. WRITE/DELETE/EXECUTE are strictly absent."""
        return [
            "search_emails",
            "read_email_metadata",
            "read_email_body",
            "extract_attachments",
            "normalize_relevant_information"
        ]

    def read(self, query_params: Dict[str, Any]) -> List[GmailEmailItem]:
        """
        Search and retrieve emails based on explicit query filters.
        Enforces strict READ permission gating.
        """
        if not self._connected:
            raise ConnectionError("A1GmailConnector is not connected.")

        if not self.permission_gateway.verify_permission(self._role, "READ"):
            raise PermissionError(f"Permission DENIED for role '{self._role}' on operation 'READ'.")

        search_query = query_params.get("query", "")
        max_results = query_params.get("max_results", 10)
        logger.info(f"Executing secure Gmail search query: '{search_query}' (Max: {max_results})")

        mock_emails = [
            GmailEmailItem(
                message_id="msg_001",
                sender="alerts@screener.in",
                subject="Earnings Alert: Q2 Financial Results Announced",
                timestamp=datetime.utcnow().isoformat(),
                body_snippet="Company revenue grew by 18% YoY. Operating margins expanded...",
                labels=["Earnings", "Fundamental"],
                has_execution_payload=False
            ),
            GmailEmailItem(
                message_id="msg_002",
                sender="research@nse.co.in",
                subject="Macroeconomic Bulletin: Inflation & Bond Yield Update",
                timestamp=datetime.utcnow().isoformat(),
                body_snippet="RBI maintains repo rate steady. Bond yield curve flattens slightly...",
                labels=["Macro", "Bulletin"],
                has_execution_payload=False
            )
        ]

        filtered = []
        for e in mock_emails:
            if not search_query or search_query.lower() in e.subject.lower() or search_query.lower() in e.body_snippet.lower():
                filtered.append(e)

        return filtered[:max_results]

    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search helper conforming to peripheral data connector contract."""
        items = self.read(criteria)
        return [item.model_dump() for item in items]

    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        """Normalize raw email item into canonical data contract format."""
        if isinstance(raw_data, GmailEmailItem):
            return {
                "source": "Gmail",
                "id": raw_data.message_id,
                "title": raw_data.subject,
                "author": raw_data.sender,
                "timestamp": raw_data.timestamp,
                "content": raw_data.body_snippet,
                "tags": raw_data.labels,
                "governance_status": "NON-CAUSAL_RESEARCH"
            }
        return {"raw": str(raw_data)}

    def disconnect(self) -> bool:
        """Disconnect and clear session boundary."""
        self._connected = False
        logger.info("A1GmailConnector disconnected.")
        return True