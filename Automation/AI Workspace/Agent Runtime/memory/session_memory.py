import json
from pathlib import Path
from typing import Dict, Any, List

class MemoryManager:
    def __init__(self, persistent_path: str = None):
        if persistent_path is None:
            persistent_path = Path(__file__).parent / "persistent_memory.json"
        self.persistent_path = Path(persistent_path)
        self.session_buffer: List[Dict[str, Any]] = []
        self._init_persistent()

    def _init_persistent(self):
        if not self.persistent_path.exists():
            default_data = {
                "user_preferences": {"preferred_style": "BTST", "risk_unit": "percentage"},
                "recurring_patterns": [],
                "workflow_state": {}
            }
            with open(self.persistent_path, "w", encoding="utf-8-sig") as f:
                json.dump(default_data, f, indent=2)

    def get_persistent_memory(self) -> Dict[str, Any]:
        with open(self.persistent_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)

    def log_session_turn(self, query: str, intent: str, tool_results: Any, final_response: str):
        self.session_buffer.append({
            "query": query,
            "intent": intent,
            "tool_results": tool_results,
            "final_response": final_response
        })

    def get_session_history() -> List[Dict[str, Any]]:
        return self.session_buffer
