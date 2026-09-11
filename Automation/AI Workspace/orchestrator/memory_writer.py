import sys
import json
from pathlib import Path
from typing import Dict, Any, Tuple

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.append(str(runtime_path / "memory"))

from session_memory import MemoryManager

class ControlledMemoryWriter:
    """
    Controlled Memory Writer enforcing state updates ONLY to L2 Session Context
    or L3 Local Json Persistence. Strictly blocks mutations to L0 System or L1 Knowledge.
    """
    MUTATION_PROTECTED_LAYERS = ["L0_SYSTEM", "L1_KNOWLEDGE", "01_RULES_AND_RISK", "04_GOVERNANCE"]

    def __init__(self):
        self.session_memory = MemoryManager()

    def write_session_log(self, target_layer: str, session_id: str, query: str, response: Dict[str, Any]) -> Tuple[bool, str]:
        # Authority Rule Enforcement
        if target_layer.upper() in self.MUTATION_PROTECTED_LAYERS:
            return False, f"AUTHORITY_DENIAL: Direct write to authoritative layer '{target_layer}' is forbidden."

        if target_layer.upper() not in ["L2_SESSION", "L3_PERSISTENT"]:
            return False, f"INVALID_LAYER: Target layer '{target_layer}' is not a valid write target."

        try:
            self.session_memory.log_session_turn(
                query=query,
                intent=response.get("intent", "UNKNOWN"),
                tool_results=response.get("skill_output"),
                final_response=json.dumps(response)
            )
            return True, f"Successfully written turn to {target_layer} for session '{session_id}'."
        except Exception as e:
            return False, f"WRITE_ERROR: Failed to write memory turn - {str(e)}"
