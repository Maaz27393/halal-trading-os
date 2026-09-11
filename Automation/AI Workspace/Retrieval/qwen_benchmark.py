import json
import time
import urllib.request
import retrieval_adapter

OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:4b"

BENCHMARK_QUERIES = [
    {"id": 1, "cat": "Governance", "query": "Who has authority to approve a change to the Trading OS?"},
    {"id": 2, "cat": "Governance", "query": "What is the halal compliance criteria for stock filtering?"},
    {"id": 3, "cat": "SOPs", "query": "What is the daily pre-market routine SOP?"},
    {"id": 4, "cat": "SOPs", "query": "How is position sizing calculated for trades?"},
    {"id": 5, "cat": "Rules", "query": "What are the mandatory exit rules for a position?"},
    {"id": 6, "cat": "Rules", "query": "What are the portfolio drawdown limits and rules?"},
    {"id": 7, "cat": "Indicators", "query": "How is VWAP used in trade setups?"},
    {"id": 8, "cat": "Indicators", "query": "What are the exact entry criteria for the EMA pullback strategy?"},
    {"id": 9, "cat": "Research", "query": "What research supports the risk-to-reward parameters?"},
    {"id": 10, "cat": "Research", "query": "What is the backtest historical win rate evidence?"}
]

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

def run_full_benchmark():
    tool_def = retrieval_adapter.get_qwen_tool_definition()
    print("=" * 80)
    print("  QWEN ↔ MCP FULL 10-QUERY SYNTHESIS BENCHMARK")
    print("=" * 80)

    results = []

    for item in BENCHMARK_QUERIES:
        qid, cat, query = item["id"], item["cat"], item["query"]
        print(f"\n[{qid}/10] Testing [{cat}]: '{query}'")
        start_time = time.time()

        messages = [
            {
                "role": "system",
                "content": "You are an assistant for the Halal Trading OS. You MUST use the vault_search tool whenever asked about trading rules or governance. Be concise and ground answers in evidence."
            },
            {"role": "user", "content": query}
        ]

        # Stage 1: Initial query to LLM
        res1 = send_ollama_request(messages, tools=[tool_def])
        msg1 = res1.get("message", {})
        tool_calls = msg1.get("tool_calls", [])

        if not tool_calls:
            print("  ❌ FAIL: No tool call generated.")
            results.append({"id": qid, "status": "FAIL_NO_TOOL", "time_ms": round((time.time() - start_time) * 1000, 1)})
            continue

        messages.append(msg1)
        
        # Stage 2: Execute retrieval
        tool_call = tool_calls[0]
        args = tool_call["function"]["arguments"]
        search_res = retrieval_adapter.query_retrieval_api(args.get("query", query))

        messages.append({
            "role": "tool",
            "content": json.dumps(search_res)
        })

        # Stage 3: Get final answer
        res2 = send_ollama_request(messages)
        final_ans = res2.get("message", {}).get("content", "")
        elapsed = round((time.time() - start_time) * 1000, 1)

        print(f"  ✅ SUCCESS ({elapsed} ms) | Conf: {search_res.get('confidence')} | Matches: {len(search_res.get('results', []))}")
        print(f"  Snippet: {final_ans[:140].replace('\n', ' ')}...")

        results.append({
            "id": qid,
            "cat": cat,
            "status": "PASS",
            "confidence": search_res.get("confidence"),
            "time_ms": elapsed
        })

    print("\n" + "=" * 80)
    print("  BENCHMARK SUMMARY")
    print("=" * 80)
    print(f"Total Queries Processed: {len(results)}")
    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"Successful Tool-Calling Loops: {passed}/{len(results)} ({passed/len(results)*100:.0f}%)")
    avg_latency = sum(r["time_ms"] for r in results) / len(results)
    print(f"Average Total Execution Time: {avg_latency:.1f} ms")
    print("=" * 80)

if __name__ == "__main__":
    run_full_benchmark()
