import sys
import json
from pathlib import Path
from typing import Dict, Any

runtime_path = Path(__file__).parent
sys.path.extend([
    str(runtime_path / "router"),
    str(runtime_path / "permissions"),
    str(runtime_path / "skills"),
    str(runtime_path / "memory")
])

from intent_router import IntentRouter
from firewall import ToolPermissionFirewall
from registry import SkillRegistry
from rule_compliance_skill import VerifyRuleComplianceSkill
from session_memory import MemoryManager

class AgentRuntime:
    def __init__(self):
        self.router = IntentRouter()
        self.firewall = ToolPermissionFirewall()
        self.memory = MemoryManager()
        self.skills = SkillRegistry()
        self._register_default_skills()

    def _register_default_skills(self):
        self.skills.register(VerifyRuleComplianceSkill())

    def process_query(self, query: str, execution_kwargs: Dict[str, Any] = None) -> Dict[str, Any]:
        execution_kwargs = execution_kwargs or {}
        
        # Step 1: Intent Routing
        route = self.router.route_query(query)
        intent = route["intent"]

        # Step 2: Skill Execution Check
        skill_output = None
        matching_skills = self.skills.get_skills_for_intent(intent)
        if matching_skills:
            for skill_name in matching_skills:
                skill_output = self.skills.execute_skill(skill_name, {}, **execution_kwargs)

        # Step 3: Tool Permission Firewall Check
        permitted_tools = route["permitted_tools"]
        firewall_logs = []
        for tool in permitted_tools:
            allowed, msg = self.firewall.validate_tool_call(intent, tool, {"query": query})
            firewall_logs.append({"tool": tool, "allowed": allowed, "message": msg})
            if not allowed:
                return {
                    "status": "BLOCKED",
                    "reason": f"Firewall blocked tool '{tool}': {msg}",
                    "intent": intent,
                    "max_authority_rank": route["max_authority_rank"],
                    "allowed_layers": route["allowed_layers"],
                    "skill_output": skill_output,
                    "firewall_checks": firewall_logs,
                    "route": route
                }

        # Step 4: Persistent Context Verification
        persistent_data = self.memory.get_persistent_memory()
        
        response_summary = f"Query routed to '{intent}' under authority rank {route['max_authority_rank']}."
        if skill_output:
            response_summary += f" Skill evaluation output: {skill_output}"

        # Step 5: Log to Session Memory
        self.memory.log_session_turn(query, intent, skill_output, response_summary)

        return {
            "status": "SUCCESS",
            "intent": intent,
            "max_authority_rank": route["max_authority_rank"],
            "allowed_layers": route["allowed_layers"],
            "firewall_checks": firewall_logs,
            "skill_output": skill_output,
            "persistent_context_loaded": bool(persistent_data),
            "response_summary": response_summary
        }

if __name__ == "__main__":
    agent = AgentRuntime()
    res = agent.process_query("What is the maximum risk per trade?")
    print(json.dumps(res, indent=2))
