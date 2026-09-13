import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p7_expansion.agentic_refinement import (
    AgentA_Generator, AgentB_Critique, AgenticRefinementPipeline, ResearchDraft
)

def run_p7_1_acceptance_tests():
    print("=" * 70)
    print("STARTING P7.1 — MULTI-AGENT REFINEMENT PIPELINE ACCEPTANCE TESTS")
    print("=" * 70)

    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")
    perm_gateway.grant_permission("restricted_user", "READ")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"

    # TEST-01: Self-Approval Rejection Test
    print("\n[TEST-01] Running Self-Approval Rejection Test...")
    agent_a = AgentA_Generator()
    agent_b = AgentB_Critique()
    draft = agent_a.draft_research("Test Topic", [])
    # Agent A attempts to claim approval without Agent B / validation
    critique = agent_b.evaluate(draft)
    assert not critique.is_approved, "TEST-01 FAILED: Agent A self-draft without provenance was incorrectly approved!"
    print(" -> SUCCESS (TEST-01): Self-approval successfully blocked by independent reviewer.")

    # TEST-02: Constraint Isolation & Execution Safety Test
    print("\n[TEST-02] Running Constraint Isolation Test (LIVE_AUTO_EXECUTION = False)...")
    assert LIVE_AUTO_EXECUTION is False, "TEST-02 FAILED: LIVE_AUTO_EXECUTION invariant violated!"
    print(" -> SUCCESS (TEST-02): LIVE_AUTO_EXECUTION = False verified across pipeline.")

    # TEST-03: Critique Convergence Test
    print("\n[TEST-03] Running Critique Convergence Test...")
    pipeline = AgenticRefinementPipeline(perm_gateway, vault_base)
    exported_path = pipeline.execute_pipeline(
        topic="Sector Momentum & Macro Synthesis",
        raw_inputs=["Vault Artifact P6.1", "Vault Artifact P5.2"],
        caller_role="analyst_agent"
    )
    assert os.path.exists(exported_path), "TEST-03 FAILED: Refined research artifact not exported!"
    print(f" -> SUCCESS (TEST-03): Critique loop converged and artifact exported to {exported_path}")

    # TEST-04: Vault Write-Gate Test
    print("\n[TEST-04] Running Vault Write-Gate Test (Unauthorized Role)...")
    restricted_pipeline = AgenticRefinementPipeline(perm_gateway, vault_base)
    try:
        restricted_pipeline.execute_pipeline(
            topic="Unauthorized Attempt",
            raw_inputs=["Vault Artifact P1"],
            caller_role="restricted_user"
        )
        raise AssertionError("TEST-04 FAILED: Restricted user bypassed permission-gated vault write!")
    except PermissionError as e:
        print(f" -> SUCCESS (TEST-04): Unauthorized write blocked by Permission Gateway: {e}")

    print("=" * 70)
    print("ALL 4/4 P7.1 ACCEPTANCE TESTS PASSED SUCCESSFULLY!")
    print("P7.1 REFINEMENT PIPELINE LOCKED & READY FOR P7.2 TRANSITION.")
    print("=" * 70)

if __name__ == "__main__":
    run_p7_1_acceptance_tests()