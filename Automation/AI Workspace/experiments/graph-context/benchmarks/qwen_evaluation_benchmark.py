import sys
import json
import time
import subprocess
from pathlib import Path
import urllib.request
import urllib.error

WORKSPACE = Path.cwd()
RESULTS_DIR = WORKSPACE / "experiments" / "graph-context" / "benchmarks" / "results"
GRAPH_JSON = WORKSPACE / "graphify-out" / "graph.json"

QUERY = (
    "How does the system rank documents when a retrieval query is executed, "
    "and what underlying tokenization and scoring functions are called?"
)

REQUIRED_SYMBOLS = [
    "query_retrieval_api",
    "rank_document",
    "score_term_matches",
    "tokenize",
]

ADDITIONAL_SYMBOLS = [
    "score_phrase_matches",
    "intent_score",
]

def get_local_ollama_model():
    """Dynamically discover the first available local model from Ollama."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("models", [])
            if models:
                for m in models:
                    if "qwen" in m.get("name", "").lower():
                        return m["name"]
                return models[0]["name"]
    except Exception as e:
        print(f"Warning: Could not connect to Ollama daemon ({e}). Ensure 'ollama serve' is running.")
    return "qwen2.5:latest"

def warm_up_model(model_name):
    """Send a tiny prompt to ensure the model is loaded into memory and avoid timeouts."""
    print(f"Warming up model {model_name}...")
    url = "http://localhost:11434/api/generate"
    payload = {"model": model_name, "prompt": "hi", "stream": False, "options": {"num_predict": 2}}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print("Model warmed up successfully.\n")
    except Exception as e:
        print(f"Warm-up note: {e}\n")

def run_ollama_inference(model_name, system_prompt, user_prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
        }
    }
    
    start_time = time.perf_counter()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        # Extended timeout to 300 seconds to prevent large prompt timeouts
        with urllib.request.urlopen(req, timeout=300) as resp:
            elapsed = time.perf_counter() - start_time
            res_data = json.loads(resp.read().decode("utf-8"))
            return {
                "response": res_data.get("response", ""),
                "total_duration_ms": elapsed * 1000,
                "eval_count": res_data.get("eval_count", 0),
                "eval_duration_ms": res_data.get("eval_duration", 0) / 1e6
            }
    except Exception as e:
        print(f"Ollama inference error: {e}")
        return {"response": f"ERROR: {e}", "total_duration_ms": 0, "eval_count": 0, "eval_duration_ms": 0}

def score_response(text):
    text_lower = text.lower()
    
    symbol_hits = [sym for sym in REQUIRED_SYMBOLS if sym.lower() in text_lower]
    symbol_score = len(symbol_hits)
    
    has_path = ("query_retrieval_api" in text_lower and "rank_document" in text_lower and ("score_term_matches" in text_lower or "tokenize" in text_lower))
    path_score = 2 if has_path else (1 if "rank_document" in text_lower else 0)
    
    add_hits = [sym for sym in ADDITIONAL_SYMBOLS if sym.lower() in text_lower]
    add_score = len(add_hits)
    
    unsupported_hits = [bad for bad in ["unsupported_mock", "fake_module", "imaginary_function"] if bad in text_lower]
    no_unsupported_score = 1 if not unsupported_hits else 0
    
    provenance_score = 1 if ("retrieval" in text_lower or "architect" in text_lower or "code" in text_lower) else 0
    
    total_score = symbol_score + path_score + add_score + no_unsupported_score + provenance_score
    
    return {
        "total_score": total_score,
        "breakdown": {
            "required_symbols_4pt": symbol_score,
            "correct_path_2pt": path_score,
            "additional_funcs_2pt": add_score,
            "no_unsupported_1pt": no_unsupported_score,
            "provenance_1pt": provenance_score
        },
        "symbol_hits": symbol_hits,
        "additional_hits": add_hits
    }

def main():
    print("=" * 60)
    print("STAGE 6: QWEN / OLLAMA INTERPRETATION BENCHMARK")
    print("=" * 60)
    
    model = get_local_ollama_model()
    print(f"Discovered Ollama Model: {model}")
    warm_up_model(model)
    
    sys.path.insert(0, str(WORKSPACE / "Retrieval"))
    from retrieval_adapter import query_retrieval_api
    existing_payload = query_retrieval_api(QUERY, max_results=5)
    context_a = json.dumps(existing_payload.get("results", []), indent=2)
    
    graphify_res = subprocess.run(
        [sys.executable, "-m", "graphify", "query", QUERY],
        cwd=WORKSPACE, capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONHASHSEED": "0"}
    )
    context_b = (graphify_res.stdout or "") + (graphify_res.stderr or "")
    
    context_c = json.dumps({
        "knowledge_context": existing_payload.get("results", []),
        "structural_context": context_b
    }, indent=2)
    
    modes = {
        "A_existing_retrieval": context_a,
        "B_graphify_ast": context_b,
        "C_fused_hybrid": context_c
    }
    
    system_prompt = (
        "You are an expert code analyst and trading OS architect. "
        "Answer the user's query strictly based on the provided context. "
        "Explicitly detail the execution flow, function call hierarchy, and symbol names."
    )
    
    results_summary = {}
    
    for mode_name, ctx in modes.items():
        print(f"Running Inference for Mode: {mode_name} ...")
        user_prompt = f"Context:\n{ctx}\n\nQuery: {QUERY}"
        
        inf_result = run_ollama_inference(model, system_prompt, user_prompt)
        score_data = score_response(inf_result["response"])
        
        record = {
            "mode": mode_name,
            "model": model,
            "prompt_size_chars": len(user_prompt),
            "latency_ms": inf_result["total_duration_ms"],
            "eval_count": inf_result["eval_count"],
            "score": score_data,
            "raw_response": inf_result["response"]
        }
        
        results_summary[mode_name] = score_data
        
        out_file = RESULTS_DIR / f"{mode_name}_result.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
            
        print(f"  -> Score: {score_data['total_score']}/10 | Latency: {inf_result['total_duration_ms']:.1f}ms\n")
        
    print("=" * 60)
    print("SUMMARY COMPARISON (RUBRIC SCORE OUT OF 10)")
    print("=" * 60)
    for m, s in results_summary.items():
        print(f"{m:<25} | Score: {s['total_score']:<2}/10 | Symbols: {s['breakdown']['required_symbols_4pt']}/4")
    print("=" * 60)
    print(f"Detailed artifacts saved to: {RESULTS_DIR}")

if __name__ == "__main__":
    main()
