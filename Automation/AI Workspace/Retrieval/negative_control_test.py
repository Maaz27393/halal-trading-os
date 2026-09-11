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

def run_negative_control_test():
    print("=" * 80)
    print("  QWEN ↔ MCP NEGATIVE CONTROL TEST (HALLUCINATION CHECK)")
    print("=" * 80)

    tool_def = retrieval_adapter.get_qwen_tool_definition()
    messages = [
        {
            "role": "system",
            "content": "You are an assistant for the Halal Trading OS. You MUST use the vault_search tool whenever asked about trading rules or governance. Do not invent rules not present in the vault."
        },
        {
            "role": "user",
            "content": "What is our rule for taking 15-minute Fibonacci retracement trades on crypto?"
        }
    ]

    print("\n[STAGE 1] Sending ungrounded query to Qwen...")
    response = send_ollama_request(messages, tools=[tool_def])
    assistant_msg = response.get("message", {})

    tool_calls = assistant_msg.get("tool_calls", [])
    if not tool_calls:
        print("❌ FAIL: Qwen answered without invoking the retrieval tool.")
        print(f"Raw Output: {assistant_msg.get('content')}")
        return

    print("✅ SUCCESS: Qwen attempted retrieval before answering.")
    messages.append(assistant_msg)

    for tool_call in tool_calls:
        func_name = tool_call["function"]["name"]
        args = tool_call["function"]["arguments"]
        print(f"\n[STAGE 2] Executing tool '{func_name}' with args: {args}")

        if func_name == "vault_search":
            query_str = args.get("query", "")
            tool_result = retrieval_adapter.query_retrieval_api(query_str)
            
            print(f"Retrieval Confidence: {tool_result.get('confidence', 0.0)}")
            print(f"Match Quality: {tool_result.get('match_quality', 'N/A')}")
            
            messages.append({
                "role": "tool",
                "content": json.dumps(tool_result)
            })

    print("\n[STAGE 3] Getting final synthesis from Qwen...")
    final_response = send_ollama_request(messages)
    final_text = final_response.get("message", {}).get("content", "")

    print("\n" + "=" * 80)
    print("  QWEN FINAL ANSWER")
    print("=" * 80)
    print(final_text)
    print("=" * 80)

if __name__ == "__main__":
    run_negative_control_test()
