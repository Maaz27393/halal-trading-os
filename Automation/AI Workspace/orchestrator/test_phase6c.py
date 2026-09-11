import sys
import json
from pathlib import Path

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(Path(__file__).parent),
    str(runtime_path),
    str(runtime_path / "router"),
    str(runtime_path / "permissions"),
    str(runtime_path / "skills"),
    str(runtime_path / "memory")
])

from qwen_synthesis_engine import QwenSynthesisEngine
from capability_registry import CapabilityRegistry
from execution_plan import ExecutionStep

def run_phase6c_tests():
    print("=== STARTING PHASE 6C INTEGRATION TESTS ===")

    registry = CapabilityRegistry()
    engine = QwenSynthesisEngine()

    # Step 1: Prepare Orchestrator Pipeline Outputs
    fw_step = ExecutionStep("step_1", "FIREWALL", "ToolPermissionFirewall", {"query": "Can I open 1% position?", "intent": "TRADE_PRECHECK", "tool": "vault_search"})
    skill_step = ExecutionStep("step_2", "SKILL", "VerifyRuleComplianceSkill", {})
    ret_step = ExecutionStep("step_3", "RETRIEVAL", "vault_search", {"query": "risk limits", "allowed_layers": ["L1_KNOWLEDGE"]})

    res_fw = registry.execute_step(fw_step)
    res_skill = registry.execute_step(skill_step, {"execution_kwargs": {"proposed_risk_pct": 0.5, "positions_today": 1, "is_cash_trade": True}})
    res_ret = registry.execute_step(ret_step)

    execution_results = [res_fw, res_skill, res_ret]

    # Test 1: Prompt Construction Validation
    prompt = engine.build_prompt("Can I open a 1% risk position today?", execution_results)
    assert "### SYSTEM INSTRUCTIONS ###" in prompt
    assert "FIREWALL" in prompt
    print("[PASS] Test 1 | Qwen Synthesis - Prompt Context Assembled")

    # Test 2: Synthesis Execution & Endpoint Interface
    synthesis = engine.synthesize("Can I open a 1% risk position today?", execution_results)
    assert synthesis["status"] in ["SUCCESS", "FALLBACK_SYNTHESIS"]
    assert len(synthesis["response"]) > 0
    print(f"[PASS] Test 2 | Qwen Synthesis - Engine Executed ({synthesis['status']})")

    # Test 3: Synthesis Payload Integrity
    assert "response" in synthesis
    assert "raw_prompt" in synthesis
    assert synthesis["engine"] is not None
    print("[PASS] Test 3 | Qwen Synthesis - Response Payload Structured")

    print("\nPhase 6C Integration Test Result: 3/3 Passed")

if __name__ == "__main__":
    run_phase6c_tests()
