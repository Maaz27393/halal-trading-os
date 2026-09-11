import time
import json
from retrieval_adapter import query_retrieval_api

# 10 Representative test queries across Governance, SOPs, BTST/Intraday Rules, and Research
BENCHMARK_QUERIES = [
    {"id": 1, "category": "Governance", "query": "Who has authority to approve a change to the Trading OS?"},
    {"id": 2, "category": "Governance", "query": "What are the compliance rules for stock screening?"},
    {"id": 3, "category": "SOPs", "query": "What is the pre-market routine checklist?"},
    {"id": 4, "category": "SOPs", "query": "How is risk per trade calculated for swing positions?"},
    {"id": 5, "category": "Rules", "query": "What are the strict exit criteria for BTST trades?"},
    {"id": 6, "category": "Rules", "query": "When is trading halted based on drawdown rules?"},
    {"id": 7, "category": "Indicators", "query": "How are EMA 20 and EMA 50 pullbacks validated?"},
    {"id": 8, "category": "Indicators", "query": "What volume spike threshold triggers a breakout setup?"},
    {"id": 9, "category": "Research", "query": "What evidence supports using VWAP for intraday entries?"},
    {"id": 10, "category": "Research", "query": "How is Fixed Range Volume Profile used for support and resistance?"},
]

def run_benchmark():
    print("=" * 80)
    print("  HALAL TRADING OS — RETRIEVAL V3.6 BENCHMARK SUITE")
    print("=" * 80)
    print(f"{'ID':<4} | {'Category':<12} | {'Confidence':<10} | {'Quality':<10} | {'Latency (ms)':<12} | {'Top Result Path'}")
    print("-" * 80)

    total_time = 0
    passed_queries = 0

    for item in BENCHMARK_QUERIES:
        start_time = time.perf_counter()
        payload = query_retrieval_api(item["query"], max_results=5)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        total_time += elapsed_ms

        confidence = payload.get("confidence", 0.0)
        match_quality = payload.get("match_quality", "N/A")
        results = payload.get("results", [])
        top_path = results[0]["path"] if results else "NO MATCH"

        if results and confidence > 0.0:
            passed_queries += 1

        print(f"{item['id']:<4} | {item['category']:<12} | {confidence:<10.2f} | {match_quality:<10} | {elapsed_ms:<12.1f} | {top_path}")

    avg_latency = total_time / len(BENCHMARK_QUERIES)
    success_rate = (passed_queries / len(BENCHMARK_QUERIES)) * 100

    print("=" * 80)
    print(f"Summary: {passed_queries}/{len(BENCHMARK_QUERIES)} queries resolved ({success_rate:.0f}% hit rate)")
    print(f"Average Retrieval Latency: {avg_latency:.2f} ms")
    print("=" * 80)

if __name__ == "__main__":
    run_benchmark()
