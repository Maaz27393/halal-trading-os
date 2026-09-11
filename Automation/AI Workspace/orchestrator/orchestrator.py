import sys
import json
from pathlib import Path
from typing import Dict, Any, List

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

from runtime import AgentRuntime
from execution_plan import ExecutionPlan, ExecutionStep
from validators import OutputValidator
from capability_registry import CapabilityRegistry
from memory_writer import ControlledMemoryWriter
from qwen_synthesis_engine import QwenSynthesisEngine

class AgentOrchestrator:
    """
    Master End-to-End Agent Orchestrator combining:
    Query -> Routing -> Planning -> Capability Execution -> Memory Writing -> Qwen Synthesis
    """
    def __init__(self):
        self.runtime = AgentRuntime()
        self.validator = OutputValidator()
        self.registry = CapabilityRegistry()
        self.memory_writer = ControlledMemoryWriter()
        self.synthesis_engine = QwenSynthesisEngine()

    def build_plan(self, query: str, route: Dict[str, Any]) -> ExecutionPlan:
        steps: List[ExecutionStep] = []
        
        # Step 1: Firewall Intercept
        steps.append(ExecutionStep(
            step_id="step_1_firewall",
            component_type="FIREWALL",
            name="ToolPermissionFirewall",
            params={"query": query, "intent": route["intent"], "tool": "vault_search"}
        ))

        # Step 2: Skill Execution if applicable
        if route["intent"] in ["TRADE_PRECHECK", "RULE_LOOKUP"]:
            steps.append(ExecutionStep(
                step_id="step_2_skill",
                component_type="SKILL",
                name="VerifyRuleComplianceSkill",
                params={"query": query}
            ))

        # Step 3: Vault Retrieval Dispatch
        if route["permitted_tools"]:
            steps.append(ExecutionStep(
                step_id="step_3_retrieval",
                component_type="RETRIEVAL",
                name="vault_search",
                params={"query": query, "allowed_layers": route["allowed_layers"]}
            ))

        return ExecutionPlan(
            query=query,
            intent=route["intent"],
            authority_rank=route["max_authority_rank"],
            allowed_layers=route["allowed_layers"],
            permitted_tools=route["permitted_tools"],
            steps=steps
        )

    def execute_orchestration(self, query: str, session_id: str = "default_session", execution_kwargs: Dict[str, Any] = None) -> Dict[str, Any]:
        execution_kwargs = execution_kwargs or {}
        
        # 1. Route Query
        route = self.runtime.router.route_query(query)
        plan = self.build_plan(query, route)

        # 2. Execute Steps via Capability Registry
        step_results = []
        for step in plan.steps:
            res = self.registry.execute_step(step, {"execution_kwargs": execution_kwargs})
            step_results.append(res)

        # 3. Firewall Intercept Check
        fw_res = next((r for r in step_results if r.get("component") == "FIREWALL"), {})
        if fw_res and not fw_res.get("allowed", False):
            blocked_payload = {
                "status": "BLOCKED",
                "orchestration_phase": "FIREWALL_INTERCEPT",
                "reason": f"Firewall blocked execution: {fw_res.get('message')}",
                "intent": route["intent"],
                "execution_plan": [s.__dict__ for s in plan.steps],
                "step_results": step_results
            }
            self.memory_writer.write_session_log("L2_SESSION", session_id, query, blocked_payload)
            return blocked_payload

        # 4. Validate Skill Output Structure
        skill_res = next((r for r in step_results if r.get("component") == "SKILL"), None)
        skill_ok, skill_msg = self.validator.validate_skill_output(skill_res)
        if not skill_ok:
            return {
                "status": "ERROR",
                "orchestration_phase": "SKILL_VALIDATION",
                "reason": skill_msg,
                "plan": plan.__dict__
            }

        # 5. Controlled Memory Logging (L2_SESSION)
        memory_ok, mem_msg = self.memory_writer.write_session_log(
            "L2_SESSION",
            session_id,
            query,
            {
                "intent": route["intent"],
                "skill_output": skill_res,
                "status": "SUCCESS"
            }
        )

        # 6. Qwen Synthesis Generation
        synthesis_res = self.synthesis_engine.synthesize(query, step_results)

        return {
            "status": "SUCCESS",
            "orchestration_phase": "COMPLETED",
            "intent": route["intent"],
            "authority_rank": route["max_authority_rank"],
            "allowed_layers": route["allowed_layers"],
            "execution_plan": [s.__dict__ for s in plan.steps],
            "step_results": step_results,
            "memory_logged": memory_ok,
            "synthesis": synthesis_res
        }

if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    res = orchestrator.execute_orchestration(
        "Can I open a trade on TATAMOTORS with 0.8% risk?",
        "test_session",
        {"proposed_risk_pct": 0.8, "positions_today": 0, "is_cash_trade": True}
    )
    print(json.dumps(res, indent=2))
