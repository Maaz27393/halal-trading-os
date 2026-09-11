import json
import urllib.request
import retrieval_adapter

OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:4b"

def send_ollama_request(messages, tools=None):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }
    if tools:
        payload["tools"] = tools

    req = urllib.request.Request(
        OLLAMA_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_qwen_tool_calling_test():
    print("=" * 80)
    print("  QWEN ↔ MCP TOOL-CALLING INTEGRATION TEST")
    print("=" * 80)

    # 1. Prepare schema & prompt
    tool_def = retrieval_adapter.get_qwen_tool_definition()
    messages = [
        {
            "role": "system",
            "content": "You are an assistant for the Halal Trading OS. You MUST use the vault_search tool whenever asked about trading rules or governance."
        },
        {
            "role": "user",
            "content": "Who has authority to approve a change to the Trading OS?"
        }
    ]

    # 2. Stage 1 & 2: Prompt Qwen & Check Tool Recognition
    print("\n[STAGE 1 & 2] Sending prompt to Qwen and checking tool invocation...")
    response = send_ollama_request(messages, tools=[tool_def])
    assistant_msg = response.get("message", {})

    tool_calls = assistant_msg.get("tool_calls", [])
    if not tool_calls:
        print("❌ FAIL: Qwen did not generate a tool call.")
        print(f"Raw Model Output: {assistant_msg.get('content')}")
        return

    print("✅ SUCCESS: Qwen recognized the tool and generated a call.")
    
    # 3. Stage 3 & 4: Execute Tool & Pass Output Back
    messages.append(assistant_msg)
    
    for tool_call in tool_calls:
        func_name = tool_call["function"]["name"]
        args = tool_call["function"]["arguments"]
        print(f"\n[STAGE 3] Executing tool '{func_name}' with args: {args}")

        if func_name == "vault_search":
            query_str = args.get("query", "")
            tool_result = retrieval_adapter.query_retrieval_api(query_str)
            
            print("✅ SUCCESS: Tool executed via retrieval adapter.")
            
            messages.append({
                "role": "tool",
                "content": json.dumps(tool_result)
            })

    # 4. Stage 5: Get Final Answer from Qwen
    print("\n[STAGE 4 & 5] Sending tool output back to Qwen for final synthesis...")
    final_response = send_ollama_request(messages)
    final_text = final_response.get("message", {}).get("content", "")

    print("\n" + "=" * 80)
    print("  QWEN FINAL ANSWER")
    print("=" * 80)
    print(final_text)
    print("=" * 80)

if __name__ == "__main__":
    run_qwen_tool_calling_test()
