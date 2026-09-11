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

from capability_registry import CapabilityRegistry
from memory_writer import ControlledMemoryWriter
from execution_plan import ExecutionStep

def run_phase6b_tests():
    print("=== STARTING PHASE 6B INTEGRATION TESTS ===")
    
    # 1. Test Capability Registry Executions
    registry = CapabilityRegistry()
    
    # Test 1A: Firewall Step
    fw_step = ExecutionStep("step_1", "FIREWALL", "ToolPermissionFirewall", {"query": "Can I trade?", "intent": "TRADE_PRECHECK"})
    res_fw = registry.execute_step(fw_step)
    assert res_fw["component"] == "FIREWALL"
    assert res_fw["allowed"] is True
    print("[PASS] Test 1A | Capability Registry - Firewall Step Executed")
    
    # Test 1B: Skill Step
    skill_step = ExecutionStep("step_2", "SKILL", "VerifyRuleComplianceSkill", {})
    res_skill = registry.execute_step(skill_step, {"execution_kwargs": {"proposed_risk_pct": 0.5, "positions_today": 1, "is_cash_trade": True}})
    assert res_skill["compliant"] is True
    print("[PASS] Test 1B | Capability Registry - Skill Step Executed")
    
    # Test 1C: Retrieval Step Dispatch
    ret_step = ExecutionStep("step_3", "RETRIEVAL", "vault_search", {"query": "risk limits", "allowed_layers": ["L0_SYSTEM", "L1_KNOWLEDGE"]})
    res_ret = registry.execute_step(ret_step)
    assert res_ret["status"] == "DISPATCHED_TO_MCP"
    print("[PASS] Test 1C | Capability Registry - Retrieval Step Executed")
    
    # 2. Test Controlled Memory Writer Protections
    writer = ControlledMemoryWriter()
    
    # Test 2A: Allowed write to L2_SESSION
    ok_l2, msg_l2 = writer.write_session_log("L2_SESSION", "test_session_001", "Can I open position?", {"status": "SUCCESS"})
    assert ok_l2 is True
    print("[PASS] Test 2A | Memory Writer - L2_SESSION Write Permitted")
    
    # Test 2B: Blocked write to L0_SYSTEM
    ok_l0, msg_l0 = writer.write_session_log("L0_SYSTEM", "test_session_001", "Modify rule", {"status": "BLOCKED"})
    assert ok_l0 is False
    assert "AUTHORITY_DENIAL" in msg_l0
    print("[PASS] Test 2B | Memory Writer - L0_SYSTEM Direct Write Blocked")
    
    # Test 2C: Blocked write to 01_RULES_AND_RISK
    ok_rules, msg_rules = writer.write_session_log("01_RULES_AND_RISK", "test_session_001", "Override rule", {"status": "BLOCKED"})
    assert ok_rules is False
    assert "AUTHORITY_DENIAL" in msg_rules
    print("[PASS] Test 2C | Memory Writer - 01_RULES_AND_RISK Direct Write Blocked")

    print("\nPhase 6B Integration Test Result: 6/6 Passed")

if __name__ == "__main__":
    run_phase6b_tests()
