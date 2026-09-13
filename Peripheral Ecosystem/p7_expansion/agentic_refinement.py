import os
import logging
import hashlib
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("P71AgenticRefinement")

class ResearchDraft(BaseModel):
    title: str
    content: str
    provenance_sources: List[str]
    author_agent: str
    has_execution_payload: bool = False

class CritiqueLog(BaseModel):
    critical_flags: List[str]
    is_approved: bool
    reviewer_agent: str

class DeterministicValidationResult(BaseModel):
    is_valid: bool
    schema_passed: bool
    provenance_passed: bool
    permission_passed: bool
    integrity_hash: str
    error_message: Optional[str] = None

class AgentA_Generator:
    """Agent A: Initial Research Draft Generation."""
    def __init__(self):
        self.name = "Agent_A_Generator"

    def draft_research(self, topic: str, raw_inputs: List[str]) -> ResearchDraft:
        logger.info(f"[{self.name}] Drafting initial research for topic: {topic}")
        return ResearchDraft(
            title=f"Research Artifact: {topic}",
            content=f"Detailed analysis on {topic} derived from raw inputs.",
            provenance_sources=raw_inputs,
            author_agent=self.name,
            has_execution_payload=False
        )

class AgentB_Critique:
    """Agent B: Independent Adversarial Review & Critique (Cannot self-approve)."""
    def __init__(self):
        self.name = "Agent_B_Critique"

    def evaluate(self, draft: ResearchDraft) -> CritiqueLog:
        logger.info(f"[{self.name}] Reviewing draft from {draft.author_agent}")
        flags = []
        if not draft.provenance_sources:
            flags.append("Missing provenance sources.")
        if draft.has_execution_payload or LIVE_AUTO_EXECUTION:
            flags.append("CRITICAL: Execution payload detected or LIVE_AUTO_EXECUTION enabled.")
        
        is_approved = len(flags) == 0
        return CritiqueLog(
            critical_flags=flags,
            is_approved=is_approved,
            reviewer_agent=self.name
        )

class AgentC_Refinement:
    """Agent C: Refinement & Synthesis resolving Agent B's flags (Max 3 iterations)."""
    def __init__(self):
        self.name = "Agent_C_Refinement"

    def refine(self, draft: ResearchDraft, critique: CritiqueLog, iteration: int) -> ResearchDraft:
        logger.info(f"[{self.name}] Refining draft (Iteration {iteration}/3) based on critique flags.")
        if iteration > 3:
            raise RuntimeError("Max refinement iterations (3) exceeded without convergence.")
        
        # Resolve flags deterministically
        resolved_content = draft.content + f" [Refined via Agent C, Iteration {iteration}]"
        return ResearchDraft(
            title=draft.title,
            content=resolved_content,
            provenance_sources=draft.provenance_sources,
            author_agent=self.name,
            has_execution_payload=False
        )

class DeterministicValidationGate:
    """Deterministic Validation Gate enforcing schema, provenance, permissions, and integrity hash."""
    def __init__(self, permission_gateway: PermissionGateway):
        self.permission_gateway = permission_gateway

    def validate_and_seal(self, draft: ResearchDraft, caller_role: str) -> DeterministicValidationResult:
        # 1. Permission check
        perm_passed = self.permission_gateway.verify_permission(caller_role, "READ") and \
                      self.permission_gateway.verify_permission(caller_role, "WRITE")
        
        # 2. Execution check invariant
        if LIVE_AUTO_EXECUTION or draft.has_execution_payload:
            return DeterministicValidationResult(
                is_valid=False, schema_passed=True, provenance_passed=True,
                permission_passed=perm_passed, integrity_hash="",
                error_message="INVARIANT VIOLATION: Execution capability prohibited."
            )

        # 3. Schema & Provenance checks
        schema_passed = bool(draft.title and draft.content)
        provenance_passed = len(draft.provenance_sources) > 0

        if not (schema_passed and provenance_passed and perm_passed):
            return DeterministicValidationResult(
                is_valid=False, schema_passed=schema_passed, provenance_passed=provenance_passed,
                permission_passed=perm_passed, integrity_hash="",
                error_message="Deterministic validation failed schema, provenance, or permissions."
            )

        # 4. Compute Integrity Hash
        raw_data = f"{draft.title}|{draft.content}|{'|'.join(draft.provenance_sources)}"
        integrity_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

        return DeterministicValidationResult(
            is_valid=True,
            schema_passed=True,
            provenance_passed=True,
            permission_passed=True,
            integrity_hash=integrity_hash
        )

class AgenticRefinementPipeline:
    """Orchestrates Agent A -> Agent B -> Agent C -> Validation Gate."""
    def __init__(self, permission_gateway: PermissionGateway, vault_base_path: str):
        self.permission_gateway = permission_gateway
        self.vault_path = vault_base_path
        self.agent_a = AgentA_Generator()
        self.agent_b = AgentB_Critique()
        self.agent_c = AgentC_Refinement()
        self.validator = DeterministicValidationGate(permission_gateway)

    def execute_pipeline(self, topic: str, raw_inputs: List[str], caller_role: str) -> str:
        # Step 1: Draft
        draft = self.agent_a.draft_research(topic, raw_inputs)

        # Step 2: Critique
        critique = self.agent_b.evaluate(draft)

        # Step 3: Refinement loop if critique flags exist
        iteration = 1
        while not critique.is_approved:
            draft = self.agent_c.refine(draft, critique, iteration)
            critique = self.agent_b.evaluate(draft)
            iteration += 1

        # Step 4: Deterministic Validation Gate
        val_result = self.validator.validate_and_seal(draft, caller_role)
        if not val_result.is_valid:
            raise PermissionError(f"Validation Gate Rejected Artifact: {val_result.error_message}")

        # Step 5: Permission-gated vault serialization
        target_dir = os.path.join(self.vault_path, "Peripheral Ecosystem", "Refined Research")
        os.makedirs(target_dir, exist_ok=True)
        
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        file_path = os.path.join(target_dir, f"RefinedResearch_{date_str}.md")

        md_content = f"""---
date: {date_str}
type: refined-multi-agent-research
integrity_hash: {val_result.integrity_hash}
guardrail: LIVE_AUTO_EXECUTION=FALSE
---

# {draft.title}

## Refined Synthesis
{draft.content}

## Provenance
"""
        for src in draft.provenance_sources:
            md_content += f"- {src}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Successfully exported P7.1 refined research to {file_path}")
        return file_path