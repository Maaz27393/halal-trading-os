import os
import sys
import json
import requests

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
sys.path.insert(0, os.path.join(VAULT_ROOT, "Peripheral Ecosystem", "operational_layer"))

from nse_mcp_server import (
    get_market_status,
    get_index_vitals,
    get_india_vix,
    get_capital_market_snapshot,
    get_advance_decline
)

TOOL_REGISTRY = {
    "get_market_status": get_market_status,
    "get_index_vitals": get_index_vitals,
    "get_india_vix": get_india_vix,
    "get_capital_market_snapshot": get_capital_market_snapshot,
    "get_advance_decline": get_advance_decline,
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_market_status",
            "description": "Retrieve current market state and summary vitals from NSE.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_index_vitals",
            "description": "Retrieve live vitals, last price, and variation for a specific index like NIFTY 50 or NIFTY BANK.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index_symbol": {"type": "string", "description": "The index symbol, e.g. NIFTY 50"}
                },
                "required": ["index_symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_india_vix",
            "description": "Retrieve current India VIX volatility index vitals.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

def run_iterative_agent_loop():
    print("=" * 60)
    print("QWEN3:4b OPTIMIZED AGENT TOOL-LOOP ACCEPTANCE TEST")
    print("=" * 60)

    # Prompt structured to encourage step-by-step or clean tool invocation
    prompt = "Check the market status first, then get NIFTY 50 index vitals."
    print(f"\n[User Prompt]: {prompt}\n")

    messages = [{"role": "user", "content": prompt}]

    turn = 1
    while turn <= 5: # Safety cap on turns
        print(f"--- [Turn {turn}] Sending conversation state to Qwen3:4b ---")
        payload = {
            "model": "qwen3:4b",
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
            "stream": False,
            "options": {"temperature": 0.1},
        }

        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json=payload,
                timeout=600,  # Extended timeout for local model inference
            )
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Ollama request failed: {e}")
            break

        message = response.json().get("message", {})
        messages.append(message)

        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            print("\n============================================================")
            print("FINAL QWEN SYNTHESIS:")
            print("============================================================")
            print(message.get("content", ""))
            print("============================================================")
            break

        print(f"\n[Turn {turn}] Tool calls requested by Qwen:")
        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            func_name = func.get("name")
            func_args = func.get("arguments") or {}

            print(f"  -> Tool: {func_name}")
            print(f"  -> Arguments: {func_args}")

            if func_name not in TOOL_REGISTRY:
                tool_result = {"error": f"Unknown tool: {func_name}"}
            else:
                try:
                    if isinstance(func_args, str):
                        func_args = json.loads(func_args)
                    
                    # Execute MCP tool locally
                    raw_result = TOOL_REGISTRY[func_name](**func_args) if func_args else TOOL_REGISTRY[func_name]()
                    
                    # Compact result to prevent context bloat for 4B model
                    tool_result = {
                        "status": raw_result.get("status", "OK"),
                        "data": raw_result.get("data", raw_result)
                    }
                    print(f"  -> Result successfully fetched and compacted.")
                except Exception as exc:
                    tool_result = {"error": str(exc)}
                    print(f"  -> Tool execution error: {exc}")

            messages.append({
                "role": "tool",
                "content": json.dumps(tool_result, ensure_ascii=False),
            })
        
        turn += 1

if __name__ == "__main__":
    run_iterative_agent_loop()