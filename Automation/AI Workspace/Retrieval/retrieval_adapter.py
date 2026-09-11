import json
import sys
from pathlib import Path

# Import frozen V3.6 retrieval search module
import vault_search

def query_retrieval_api(query: str, max_results: int = 10) -> dict:
    """
    Deterministic interface adapter for Retrieval V3.6.
    Converts raw V3.6 search results into a clean, JSON-serializable agent payload.
    """
    documents, diagnostics = vault_search.load_documents()
    intent = vault_search.detect_intent(query)
    query_topics = set(vault_search.detect_topics(query))

    ranked = []
    for doc in documents:
        result = vault_search.rank_document(doc, query, intent, query_topics)
        result["_query"] = query

        lexical_relevance = (
            result["term"]
            + result["partial"]
            + result["phrase"]
            + (1 if result["topic"] > 0 else 0)
        )

        if lexical_relevance > 0 or result["score"] > vault_search.AUTHORITY_WEIGHTS.get(doc["type"], 0) + 10:
            ranked.append(result)

    # Force governance inclusion if applicable
    if intent in {"conflict", "decision", "change_control"}:
        for doc in documents:
            result = vault_search.rank_document(doc, query, intent, query_topics)
            result["_query"] = query
            if vault_search.is_authority_candidate(result, intent):
                if not any(r["path"] == result["path"] for r in ranked):
                    ranked.append(result)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    final_results = ranked[:max_results]

    match_quality = vault_search.calculate_match_quality(final_results, query, intent)
    confidence = vault_search.calculate_confidence(final_results, query, intent)

    public_results = [vault_search.public_result(r) for r in final_results]
    evidence_map = vault_search.structured_evidence(final_results)

    payload = {
        "api_version": "1.0",
        "retrieval_version": "3.6",
        "query": query,
        "intent": intent,
        "confidence": round(confidence, 2),
        "match_quality": match_quality,
        "structured_evidence": evidence_map,
        "results": public_results,
        "vault_status": {
            "files_seen": diagnostics["files_seen"],
            "files_loaded": diagnostics["files_loaded"],
            "files_skipped": diagnostics["files_skipped"],
        },
    }

    return payload

def get_qwen_tool_definition() -> dict:
    """Returns OpenAI/Qwen compatible JSON schema definition for tool calling."""
    return {
        "type": "function",
        "function": {
            "name": "vault_search",
            "description": "Searches the Halal Trading OS Obsidian vault for rules, governance, strategies, and research evidence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question to retrieve context for.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of ranked search results to return (default: 10).",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        },
    }

if __name__ == "__main__":
    test_query = sys.argv[1] if len(sys.argv) > 1 else "Who has authority to approve a change to the Trading OS?"
    response = query_retrieval_api(test_query)
    print(json.dumps(response, indent=2))
