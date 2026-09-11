import sys
from pathlib import Path
from typing import Dict, Any, Callable

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(runtime_path),
    str(runtime_path / "permissions"),
    str(runtime_path / "skills"),
    str(runtime_path / "memory")
])

from firewall import ToolPermissionFirewall
from rule_compliance_skill import VerifyRuleComplianceSkill
from execution_plan import ExecutionStep

class CapabilityRegistry:
    """
    Registry for execution components mapped to Orchestration steps.
    Safely routes execution without bypassing Firewall or Skill logic.
    """
    def __init__(self):
        self.firewall = ToolPermissionFirewall()
        self.skill = VerifyRuleComplianceSkill()
        self._handlers: Dict[str, Callable] = {
            "FIREWALL": self._exec_firewall,
            "SKILL": self._exec_skill,
            "RETRIEVAL": self._exec_retrieval,
            "MEMORY": self._exec_memory
        }

    def _exec_firewall(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        intent = params.get("intent", "UNKNOWN")
        tool = params.get("tool", "vault_search")
        allowed, msg = self.firewall.validate_tool_call(intent, tool, {"query": query})
        return {
            "component": "FIREWALL",
            "allowed": allowed,
            "message": msg,
            "intent": intent
        }

    def _exec_skill(self, params: Dict[str, Any]) -> Dict[str, Any]:
        execution_kwargs = params.get("execution_kwargs", {})
        if isinstance(execution_kwargs, dict):
            res = self.skill.execute(execution_kwargs, **execution_kwargs)
        else:
            res = self.skill.execute(execution_kwargs)
        if isinstance(res, dict):
            res["component"] = "SKILL"
        return res

    def _exec_retrieval(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "component": "RETRIEVAL",
            "query": params.get("query", ""),
            "allowed_layers": params.get("allowed_layers", []),
            "status": "DISPATCHED_TO_MCP"
        }

    def _exec_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "component": "MEMORY",
            "action": params.get("action", "READ"),
            "layer": params.get("layer", "L2_SESSION")
        }

    def execute_step(self, step: ExecutionStep, runtime_context: Dict[str, Any] = None) -> Dict[str, Any]:
        handler = self._handlers.get(step.component_type)
        if not handler:
            raise ValueError(f"Unknown component_type in registry: {step.component_type}")
        
        params = dict(step.params)
        if runtime_context:
            params["execution_kwargs"] = runtime_context.get("execution_kwargs", {})
            
        return handler(params)
