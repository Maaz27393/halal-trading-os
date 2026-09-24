from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any, Dict, List

from contracts.context_contracts import ContextBundle


class QwenRuntime:
    """
    Consumes strictly a validated ContextBundle, formats context and query,
    and queries the local Ollama/Qwen runtime. Fails closed if integrity fails.
    Read-only: does not modify state or execute tools.
    """

    def __init__(
        self,
        model_name: str = "qwen3:4b",
        ollama_endpoint: str = "http://localhost:11434/api/generate",
        timeout_seconds: int = 600,
    ):
        self.model_name = model_name
        self.ollama_endpoint = ollama_endpoint
        self.timeout_seconds = timeout_seconds

    def generate(self, bundle: ContextBundle) -> Dict[str, Any]:
        # Fail closed rule: Do not execute if Integrity Gate failed
        if not bundle.is_valid:
            raise ValueError(
                f"Integrity Gate check failed (Status: {bundle.integrity_report.get('status')}). "
                "Refusing model generation."
            )

        prompt = self._build_prompt(bundle)

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.ollama_endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
                result_json = json.loads(response_body)
                
                generated_text = result_json.get("response", "")
                
                return {
                    "status": "SUCCESS",
                    "model": self.model_name,
                    "response": generated_text,
                    "provenance": bundle.provenance,
                    "metadata": {
                        "total_duration": result_json.get("total_duration"),
                        "eval_count": result_json.get("eval_count"),
                    },
                }

        except urllib.error.URLError as exc:
            return {
                "status": "ERROR",
                "model": self.model_name,
                "response": "",
                "provenance": bundle.provenance,
                "errors": [f"Failed to connect to local Ollama endpoint ({self.ollama_endpoint}): {exc}"],
            }
        except Exception as exc:
            return {
                "status": "ERROR",
                "model": self.model_name,
                "response": "",
                "provenance": bundle.provenance,
                "errors": [f"Unexpected error during Qwen generation: {exc}"],
            }

    @staticmethod
    def _build_prompt(bundle: ContextBundle) -> str:
        query = bundle.request.user_query
        knowledge = bundle.knowledge_context
        memory = bundle.memory_context
        code = bundle.code_context

        prompt_parts = [
            "### SYSTEM INSTRUCTION ###",
            "You are a rigorous, read-only AI assistant for the Halal Trading OS.",
            "Answer the user query strictly using the provided context below. Do not assume facts not present.",
            "",
            f"### USER QUERY ###",
            query,
            "",
            "### KNOWLEDGE CONTEXT (Obsidian / Retrieval V3.6) ###",
            json.dumps(knowledge, indent=2, ensure_ascii=False) if knowledge else "No knowledge context retrieved.",
            "",
            "### MEMORY CONTEXT ###",
            json.dumps(memory, indent=2, ensure_ascii=False) if memory else "No memory context retrieved.",
            "",
            "### CODE & STRUCTURAL CONTEXT (Graphify) ###",
            json.dumps(code, indent=2, ensure_ascii=False) if code else "No code context retrieved.",
            "",
            "### RESPONSE ###"
        ]

        return "\n".join(prompt_parts)
