import sys
import json
import time
import subprocess
from pathlib import Path
import urllib.request

WORKSPACE = Path.cwd()
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

def get_local_ollama_model():
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
    except Exception:
        pass
    return "qwen2.5:latest"

def run_ollama_inference(model_name, system_prompt, user_prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    start = time.perf_counter()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            elapsed = time.perf_counter() - start
            res_data = json.loads(resp.read().decode("utf-8"))
            return {
                "response": res_data.get("response", ""),
                "total_duration_ms": elapsed * 1000,
                "prompt_eval_duration_ms": res_data.get("prompt_eval_duration", 0) / 1e6,
                "eval_duration_ms": res_data.get("eval_duration", 0) / 1e6,
                "prompt_eval_count": res_data.get("prompt_eval_count", 0),
                "eval_count": res_data.get("eval_count", 0)
            }
    except Exception as e:
        return {
            "response": f"ERROR: {e}",
            "total_duration_ms": 0,
            "prompt_eval_duration_ms": 0,
            "eval_duration_ms": 0,
            "prompt_eval_count": 0,
            "eval_count": 0
        }

def score_response(text):
    text_lower = text.lower()
    symbol_hits = [sym for sym in REQUIRED_SYMBOLS if sym.lower() in text_lower]
    symbol_score = len(symbol_hits)
    has_path = ("query_retrieval_api" in text_lower and "rank_document" in text_lower and ("score_term_matches" in text_lower or "tokenize" in text_lower))
    path_score = 2 if has_path else (1 if "rank_document" in text_lower else 0)
    add_hits = [sym for sym in ["score_phrase_matches", "intent_score"] if sym.lower() in text_lower]
    add_score = len(add_hits)
    no_unsupported = 1 if not any(b in text_lower for b in ["unsupported_mock", "fake_module"]) else 0
    provenance = 1 if ("retrieval" in text_lower or "architect" in text_lower or "code" in text_lower) else 0
    
    return {
        "total_score": symbol_score + path_score + add_score + no_unsupported + provenance,
        "symbol_hits_count": symbol_score
    }

def verify_integrity(context_text, label):
    """Integrity Gate: Guarantee 100% symbol and provenance preservation."""
    text_lower = context_text.lower()
    missing = [sym for sym in REQUIRED_SYMBOLS if sym not in text_lower]
    if missing:
        raise ValueError(f"INTEGRITY GATE FAIL [{label}]: Context dropped required symbols: {missing}")
    return True

def deterministic_optimize_graphify(raw_text):
    """Lossless Graphify text optimization: Remove excessive blank lines without truncation."""
    lines = raw_text.splitlines()
    optimized = [l.strip() for l in lines if l.strip()]
    return "\n".join(optimized)

def deterministic_optimize_fused(raw_json_str):
    """Lossless Fused JSON optimization: Minify JSON structure without dropping fields or truncation."""
    try:
        data = json.loads(raw_json_str)
        # Minify JSON representation completely (zero information loss, removes whitespace formatting)
        return json.dumps(data, separators=(',', ':'))
    except Exception:
        return raw_json_str

def main():
    print("=" * 60)
    print("STAGE 7A: DETERMINISTIC CONTEXT OPTIMIZATION WITH INTEGRITY GATE")
    print("=" * 60)
    
    model = get_local_ollama_model()
    print(f"Model: {model}\n")
    
    # 1. Gather Raw Contexts
    graphify_res = subprocess.run(
        [sys.executable, "-m", "graphify", "query", QUERY],
        cwd=WORKSPACE, capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONHASHSEED": "0"}
    )
    raw_graphify = (graphify_res.stdout or "") + (graphify_res.stderr or "")
    
    sys.path.insert(0, str(WORKSPACE / "Retrieval"))
    from retrieval_adapter import query_retrieval_api
    existing_payload = query_retrieval_api(QUERY, max_results=5)
    
    raw_fused = json.dumps({
        "knowledge_context": existing_payload.get("results", []),
        "structural_context": raw_graphify
    }, indent=2)
    
    # 2. Generate Optimized Contexts
    opt_graphify = deterministic_optimize_graphify(raw_graphify)
    opt_fused = deterministic_optimize_fused(raw_fused)
    
    # 3. Run Integrity Gate Check on all variants
    print("Running Integrity Gates...")
    verify_integrity(raw_graphify, "B0 Raw Graphify")
    verify_integrity(opt_graphify, "B1 Optimized Graphify")
    verify_integrity(raw_fused, "C0 Raw Fused")
    verify_integrity(opt_fused, "C1 Optimized Fused")
    print("All contexts passed Integrity Gate successfully.\n")
    
    variants = {
        "B0_raw_graphify": (raw_graphify, "Graphify Raw (B0)"),
        "B1_opt_graphify": (opt_graphify, "Graphify Optimized (B1)"),
        "C0_raw_fused": (raw_fused, "Fused Raw (C0)"),
        "C1_opt_fused": (opt_fused, "Fused Optimized (C1)")
    }
    
    system_prompt = "You are an expert code analyst and trading OS architect. Answer strictly based on the provided context, detailing execution flow and symbol names."
    
    summary = {}
    
    for key, (ctx_text, label) in variants.items():
        print(f"Running Inference for [{label}] (Chars: {len(ctx_text):,})...")
        user_prompt = f"Context:\n{ctx_text}\n\nQuery: {QUERY}"
        
        telemetry = run_ollama_inference(model, system_prompt, user_prompt)
        score = score_response(telemetry["response"])
        
        summary[key] = {
            "label": label,
            "size_chars": len(ctx_text),
            "prompt_tokens": telemetry["prompt_eval_count"],
            "score": score["total_score"],
            "symbols": score["symbol_hits_count"],
            "total_ms": telemetry["total_duration_ms"],
            "eval_ms": telemetry["eval_duration_ms"]
        }
        print(f"  -> Score: {score['total_score']}/10 | Symbols: {score['symbol_hits_count']}/4 | Tokens: {telemetry['prompt_eval_count']} | Time: {telemetry['total_duration_ms']/1000:.1f}s\n")
        
    print("=" * 80)
    print("STAGE 7A SUMMARY COMPARISON (RAW VS OPTIMIZED)")
    print("=" * 80)
    print(f"{'Variant':<26} | {'Chars':<8} | {'Tokens':<8} | {'Score':<6} | {'Symbols':<8} | {'Total Time (s)'}")
    print("-" * 80)
    for k, v in summary.items():
        print(f"{v['label']:<26} | {v['size_chars']:<8,d} | {v['prompt_tokens']:<8,d} | {v['score']}/10   | {v['symbols']}/4      | {v['total_ms']/1000:<8.1f}s")
    print("=" * 80)

if __name__ == "__main__":
    main()
