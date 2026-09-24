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

PONYTAIL_SKILL = (
    "\n\n[PONYTAIL BEHAVIORAL SKILL: LAZY SENIOR DEV & YAGNI PRINCIPLE]\n"
    "Before writing any explanation or code, follow the ladder of laziness:\n"
    "1. Does this need to exist at all?\n"
    "2. Is it already in the codebase/context?\n"
    "3. Can standard library or native features handle it?\n"
    "4. Can it be expressed as a direct, minimal one-liner or direct execution path?\n"
    "Write the absolute minimum text and code required to answer accurately. "
    "Eliminate all fluff, filler prose, redundant wrappers, and over-engineering. "
    "Lazy, not negligent: Maintain 100% fidelity to required symbols, dependency paths, and governance constraints."
)

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
                "prompt_eval_count": res_data.get("prompt_eval_count", 0),
                "eval_count": res_data.get("eval_count", 0)
            }
    except Exception as e:
        return {
            "response": f"ERROR: {e}",
            "total_duration_ms": 0,
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
    
    # YAGNI Compliance heuristic: Penalize chatty filler phrases, reward direct structural conciseness
    fluff_words = ["furthermore", "in conclusion", "it is important to note", "overall, the system"]
    fluff_count = sum(1 for f in fluff_words if f in text_lower)
    yagni_compliance = "PASS" if fluff_count == 0 and len(text.split()) < 350 else "REVIEW"
    
    return {
        "total_score": symbol_score + path_score + add_score + no_unsupported + provenance,
        "symbol_hits_count": symbol_score,
        "yagni": yagni_compliance,
        "word_count": len(text.split())
    }

def deterministic_optimize_graphify(raw_text):
    lines = raw_text.splitlines()
    return "\n".join([l.strip() for l in lines if l.strip()])

def main():
    print("=" * 60)
    print("STAGE 7B: PONYTAIL BEHAVIORAL PROMPT EXPERIMENT")
    print("=" * 60)
    
    model = get_local_ollama_model()
    print(f"Model: {model}\n")
    
    # Gather Frozen Contexts
    graphify_res = subprocess.run(
        [sys.executable, "-m", "graphify", "query", QUERY],
        cwd=WORKSPACE, capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONHASHSEED": "0"}
    )
    raw_graphify = (graphify_res.stdout or "") + (graphify_res.stderr or "")
    b1_graphify = deterministic_optimize_graphify(raw_graphify)
    
    sys.path.insert(0, str(WORKSPACE / "Retrieval"))
    from retrieval_adapter import query_retrieval_api
    existing_payload = query_retrieval_api(QUERY, max_results=5)
    c0_fused = json.dumps({
        "knowledge_context": existing_payload.get("results", []),
        "structural_context": raw_graphify
    }, indent=2)
    
    base_system = "You are an expert code analyst and trading OS architect. Answer strictly based on the provided context, detailing execution flow and symbol names."
    ponytail_system = base_system + PONYTAIL_SKILL
    
    experiments = {
        "B1_Control": (b1_graphify, base_system, "Graphify B1 (Control)"),
        "B1_Treatment": (b1_graphify, ponytail_system, "Graphify B1 + Ponytail"),
        "C0_Control": (c0_fused, base_system, "Fused C0 (Control)"),
        "C0_Treatment": (c0_fused, ponytail_system, "Fused C0 + Ponytail")
    }
    
    summary = {}
    
    for key, (ctx_text, sys_prompt, label) in experiments.items():
        print(f"Running Inference for [{label}]...")
        user_prompt = f"Context:\n{ctx_text}\n\nQuery: {QUERY}"
        
        telemetry = run_ollama_inference(model, sys_prompt, user_prompt)
        score = score_response(telemetry["response"])
        
        summary[key] = {
            "label": label,
            "score": score["total_score"],
            "symbols": score["symbol_hits_count"],
            "words": score["word_count"],
            "yagni": score["yagni"],
            "total_s": telemetry["total_duration_ms"] / 1000
        }
        print(f"  -> Score: {score['total_score']}/10 | Symbols: {score['symbol_hits_count']}/4 | Words: {score['word_count']} | YAGNI: {score['yagni']} | Time: {summary[key]['total_s']:.1f}s\n")
        
    print("=" * 85)
    print("STAGE 7B SUMMARY COMPARISON (CONTROL VS PONYTAIL TREATMENT)")
    print("=" * 85)
    print(f"{'Condition':<28} | {'Score':<6} | {'Symbols':<8} | {'Words':<8} | {'YAGNI':<8} | {'Time (s)'}")
    print("-" * 85)
    for k, v in summary.items():
        print(f"{v['label']:<28} | {v['score']}/10   | {v['symbols']}/4      | {v['words']:<8} | {v['yagni']:<8} | {v['total_s']:<8.1f}")
    print("=" * 85)

if __name__ == "__main__":
    main()
