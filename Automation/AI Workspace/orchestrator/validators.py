from typing import Dict, Any, Tuple

class OutputValidator:
    @staticmethod
    def validate_firewall_status(firewall_checks: list) -> Tuple[bool, str]:
        for check in firewall_checks:
            if not check.get("allowed", False):
                return False, f"FIREWALL_DENIAL: Tool '{check.get('tool')}' blocked - {check.get('message')}"
        return True, "Firewall check passed."

    @staticmethod
    def validate_skill_output(skill_output: Dict[str, Any]) -> Tuple[bool, str]:
        if skill_output is None:
            return True, "No skill executed."
        if not isinstance(skill_output, dict):
            return False, "VALIDATION_FAILED: Skill output must be a dictionary."
        if "compliant" not in skill_output:
            return False, "VALIDATION_FAILED: Skill output missing 'compliant' boolean field."
        return True, "Skill output validated successfully."

    @staticmethod
    def validate_authority_hierarchy(claimed_layer: str, max_authority_rank: int, allowed_layers: list) -> Tuple[bool, str]:
        if claimed_layer not in allowed_layers:
            return False, f"AUTHORITY_VIOLATION: Layer '{claimed_layer}' not in allowed layers {allowed_layers}"
        return True, "Authority hierarchy verified."
