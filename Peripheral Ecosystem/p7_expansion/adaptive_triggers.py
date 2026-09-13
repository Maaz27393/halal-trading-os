import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Callable
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p7_expansion.agentic_refinement import AgenticRefinementPipeline

logger = logging.getLogger("P72AdaptiveTriggers")

class EventTriggerObserver:
    """
    P7.2 Expansion: Non-invasive event observer that listens for macro or market
    variance and triggers the P7.1 multi-agent pipeline securely.
    """

    def __init__(self, permission_gateway: PermissionGateway, vault_base_path: str):
        self.permission_gateway = permission_gateway
        self.vault_path = vault_base_path
        self.refinement_pipeline = AgenticRefinementPipeline(permission_gateway, vault_base_path)
        logger.info("EventTriggerObserver initialized for P7.2.")

    def process_incoming_event(self, event_type: str, event_payload: Dict[str, Any], caller_role: str = "analyst_agent") -> str:
        """
        1. Verify immutable execution guardrail.
        2. Evaluate event significance.
        3. Dispatch to P7.1 multi-agent refinement pipeline upon validation.
        """
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")

        logger.info(f"Received event trigger [{event_type}]. Evaluating adaptive response...")

        # Map event type to research topic and sources
        if event_type == "MACRO_VARIANCE_ALERT":
            topic = f"Macro Intelligence Variance: {event_payload.get('indicator', 'Unknown')}"
            raw_sources = [f"Macro Feed Data: {event_payload.get('details', 'N/A')}"]
        elif event_type == "SCHEDULED_RESEARCH_PULSE":
            topic = "Scheduled Ecosystem Intelligence Pulse"
            raw_sources = ["Vault Cross-Reference Snapshot P5.3", "Sector Rotation P6.1"]
        else:
            topic = f"General Event Observation: {event_type}"
            raw_sources = [f"Event Payload Hash: {str(event_payload)}"]

        # Secure dispatch through P7.1 pipeline
        exported_path = self.refinement_pipeline.execute_pipeline(
            topic=topic,
            raw_inputs=raw_sources,
            caller_role=caller_role
        )

        logger.info(f"Event trigger successfully processed and exported to {exported_path}")
        return exported_path