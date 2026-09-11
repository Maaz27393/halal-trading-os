import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

# Ensure router schema imports resolve cleanly
router_path = Path(__file__).parent.parent / "router"
if str(router_path) not in sys.path:
    sys.path.append(str(router_path))

from intent_schemas import INTENT_PERMISSIONS, IntentCategory

class ToolPermissionFirewall:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "authority_rules.json"
        
        with open(config_path, "r", encoding="utf-8-sig") as f:
            self.authority_rules = json.load(f)["layers"]

    def validate_tool_call(
        self, 
        intent: str, 
        tool_name: str, 
        tool_args: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Interprets and validates whether an intended tool call aligns with
        the routed Intent Category and Authority Layer rules.
        """
        tool_args = tool_args or {}
        
        # 1. Resolve Intent Enum
        try:
            intent_enum = IntentCategory(intent)
        except ValueError:
            return False, f"FIREWALL_DENY: Unrecognized intent category '{intent}'"

        intent_cfg = INTENT_PERMISSIONS[intent_enum]

        # 2. Check Tool Permissibility
        if tool_name not in intent_cfg.permitted_tools:
            return False, (
                f"FIREWALL_DENY: Tool '{tool_name}' is NOT permitted for intent '{intent}'. "
                f"Allowed tools: {intent_cfg.permitted_tools}"
            )

        # 3. Check Write Guard / Mutation Boundaries
        if tool_name == "vault_search":
            query = str(tool_args.get("query", "")).lower()
            for mutating_word in ["write", "update", "delete", "overwrite", "modify", "append"]:
                if f" {mutating_word} " in f" {query} ":
                    return False, f"FIREWALL_DENY: Mutation keyword '{mutating_word}' prohibited during vault_search"

        # 4. Enforce Authority Rank Bounds
        required_rank = intent_cfg.max_authority_rank
        if required_rank > 4 or required_rank < 1:
            return False, f"FIREWALL_DENY: Invalid authority rank configuration ({required_rank})"

        return True, "FIREWALL_ALLOW: Tool call validated successfully"

if __name__ == "__main__":
    firewall = ToolPermissionFirewall()
    
    # Test 1: Valid RULE_LOOKUP
    a1, m1 = firewall.validate_tool_call("RULE_LOOKUP", "vault_search", {"query": "risk rules"})
    print(f"Test 1 (Valid): {m1} (Allowed={a1})")

    # Test 2: Blocked Tool for GENERAL_KNOWLEDGE
    a2, m2 = firewall.validate_tool_call("GENERAL_KNOWLEDGE", "vault_search", {"query": "hello"})
    print(f"Test 2 (Unauthorized Tool): {m2} (Allowed={a2})")

    # Test 3: Blocked Mutating Action
    a3, m3 = firewall.validate_tool_call("RULE_LOOKUP", "vault_search", {"query": "update risk rules"})
    print(f"Test 3 (Mutation Intercept): {m3} (Allowed={a3})")
