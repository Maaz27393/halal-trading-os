import os
import logging
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("ContextPromptManager")

class SanitizedContextPacket(BaseModel):
    query_topic: str
    abstracted_prompt: str
    token_budget_allocated: int
    provenance_bindings: List[str]
    guardrail_status: bool

class ContextPromptManager:
    """
    P7.3 Expansion: Model-agnostic context manager that sanitizes and structures
    cross-vault queries for local intelligence consumption without execution authority.
    """

    def __init__(self, permission_gateway: PermissionGateway, vault_base_path: str):
        self.permission_gateway = permission_gateway
        self.vault_path = vault_base_path
        logger.info("ContextPromptManager initialized for P7.3.")

    def prepare_context_packet(self, topic: str, raw_context_notes: List[str], caller_role: str = "analyst_agent") -> SanitizedContextPacket:
        """
        1. Verify read/write permission via Permission Gateway.
        2. Ensure LIVE_AUTO_EXECUTION is strictly False.
        3. Abstract and sanitize context notes into a structured prompt packet.
        """
        if not self.permission_gateway.verify_permission(caller_role, "READ"):
            raise PermissionError(f"Caller role '{caller_role}' lacks READ permission for context abstraction.")

        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")

        logger.info(f"Structuring abstracted prompt packet for topic: '{topic}'")

        # Build sanitized prompt structure
        sanitized_notes = "\n".join([f"- [Vault Ref]: {note}" for note in raw_context_notes])
        abstracted_prompt = f"""[ANALYTICAL CONTEXT PACKET]
Topic: {topic}
Constraints: LIVE_AUTO_EXECUTION = FALSE (Non-causal analytical intelligence only).
Provided Vault Notes:
{sanitized_notes}
Instructions: Synthesize insights strictly from provided context. Zero execution authority.
"""

        packet = SanitizedContextPacket(
            query_topic=topic,
            abstracted_prompt=abstracted_prompt,
            token_budget_allocated=len(abstracted_prompt.split()) * 2,  # Approximate token metric
            provenance_bindings=raw_context_notes,
            guardrail_status=LIVE_AUTO_EXECUTION
        )

        logger.info(f"Context packet successfully prepared. Token budget: {packet.token_budget_allocated}")
        return packet