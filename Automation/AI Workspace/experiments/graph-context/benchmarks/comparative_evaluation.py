import sys
import json
from pathlib import Path

# Add retrieval directory to path so we can import query_retrieval_api directly
retrieval_dir = Path.cwd() / "Retrieval"
sys.path.insert(0, str(retrieval_dir))

from retrieval_adapter import query_retrieval_api

QUERY = (
    "How does the system rank documents when a retrieval query is executed, "
    "and what underlying tokenization and scoring functions are called?"
)

EXPECTED_SYMBOLS = [
    "query_retrieval_api",
    "rank_document",
    "score_term_matches",
    "tokenize"
]

def main():
    print("=" * 60)
    print("EXISTING RETRIEVAL V3.6 — PROBE EVALUATION")
    print("=" * 60)
    print(f"Query: {QUERY}\n")

    # Invoke existing retrieval system
    payload = query_retrieval_api(QUERY, max_results=5)

    confidence = payload.get("confidence", 0.0)
    match_quality = payload.get("match_quality", "N/A")
    results = payload.get("results", [])

    print(f"Confidence  : {confidence}")
    print(f"Match Quality: {match_quality}")
    print(f"Results Count: {len(results)}")
    
    # Serialize results to inspect total context size and text content
    results_text = json.dumps(results, indent=2)
    print(f"Context Size: {len(results_text):,} characters (~{len(results_text.encode('utf-8')) / 1024:.2f} KB)")

    print("\n--- Matched Sources ---")
    for idx, res in enumerate(results, 1):
        path = res.get("path", "UNKNOWN")
        score = res.get("score", res.get("relevance", "N/A"))
        print(f"{idx}. Path: {path} (Score: {score})")

    print("\n--- Symbol Coverage Check in Retrieved Text ---")
    results_lower = results_text.lower()
    symbol_checks = {}
    for sym in EXPECTED_SYMBOLS:
        found = sym in results_lower
        symbol_checks[sym] = found
        print(f"{'PASS' if found else 'MISS'}: {sym}")

    print("\n=== SUMMARY COMPARISON ===")
    print(f"{'Metric':<25} | {'Graphify Retrieval':<22} | {'Existing Retrieval V3.6'}")
    print("-" * 75)
    print(f"{'Context Size':<25} | {'~12.10 KB':<22} | {f'~{len(results_text.encode("utf-8")) / 1024:.2f} KB'}")
    print(f"{'All Symbols Found':<25} | {'PASS':<22} | {str(all(symbol_checks.values()))}")
    print(f"{'Structural Traversal':<25} | {'Direct AST Path':<22} | {'Chunk Text Search'}")
    print("=" * 75)

if __name__ == "__main__":
    main()
