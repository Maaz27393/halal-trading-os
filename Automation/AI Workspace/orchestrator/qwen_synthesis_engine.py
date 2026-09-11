import json
import urllib.request
from typing import Dict, Any, List, Optional

class QwenSynthesisEngine:
    """
    Synthesis engine utilizing local Qwen model (via Ollama/vLLM REST API)
    to compose structured, context-aware responses based on orchestrator execution outputs.
    """
    def __init__(self, api_url: str = "http://localhost:11434/api/generate", model_name: str = "qwen2.5:coder"):
        self.api_url = api_url
        self.model_name = model_name

    def build_prompt(self, user_query: str, execution_results: List[Dict[str, Any]], session_context: Optional[Dict[str, Any]] = None) -> str:
        context_str = json.dumps(execution_results, indent=2)
        prompt = (
            "### SYSTEM INSTRUCTIONS ###\n"
            "You are the Halal Trading OS Local Synthesis Engine.\n"
            "Analyze the provided execution step results, skill evaluations, and permission checks "
            "to formulate a definitive, rule-compliant response.\n\n"
            f"### EXECUTION CONTEXT ###\n{context_str}\n\n"
            f"### USER QUERY ###\n{user_query}\n\n"
            "### SYNTHESIZED RESPONSE ###\n"
        )
        return prompt

    def synthesize(self, user_query: str, execution_results: List[Dict[str, Any]], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = self.build_prompt(user_query, execution_results, session_context)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        
        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                response_text = res_data.get("response", "")
                return {
                    "status": "SUCCESS",
                    "engine": f"Local Qwen ({self.model_name})",
                    "response": response_text,
                    "raw_prompt": prompt
                }
        except Exception as e:
            return {
                "status": "FALLBACK_SYNTHESIS",
                "engine": "Offline Deterministic Synthesizer",
                "error": str(e),
                "response": self._offline_fallback_synthesis(user_query, execution_results),
                "raw_prompt": prompt
            }

    def _offline_fallback_synthesis(self, user_query: str, execution_results: List[Dict[str, Any]]) -> str:
        skill_res = next((r for r in execution_results if r.get("component") == "SKILL"), {})
        fw_res = next((r for r in execution_results if r.get("component") == "FIREWALL"), {})
        
        is_compliant = skill_res.get("compliant", True)
        is_allowed = fw_res.get("allowed", True)
        
        status_str = "APPROVED" if (is_compliant and is_allowed) else "BLOCKED / NON-COMPLIANT"
        return f"[LOCAL SYNTHESIS FALLBACK] Query: '{user_query}' | Status: {status_str} | Execution Steps Verified: {len(execution_results)}"
