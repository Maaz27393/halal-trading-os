import json
import subprocess
import sys
from pathlib import Path

import networkx as nx


QUERY = (
    "How does the system rank documents when a retrieval query is executed, "
    "and what underlying tokenization and scoring functions are called?"
)

EXPECTED_CHAIN = [
    "retrieval_retrieval_adapter_query_retrieval_api",
    "retrieval_vault_search_rank_document",
    "retrieval_vault_search_score_term_matches",
    "retrieval_vault_search_tokenize",
]

EXPECTED_ADDITIONAL = [
    "retrieval_vault_search_score_phrase_matches",
    "retrieval_vault_search_intent_score",
]

WORKSPACE = Path.cwd()
GRAPH_JSON = WORKSPACE / "graphify-out" / "graph.json"


def load_graph():
    with GRAPH_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f)

    graph = nx.MultiDiGraph()

    for node in data.get("nodes", []):
        node_id = node.get("id")
        if node_id:
            attrs = dict(node)
            attrs.pop("id", None)
            graph.add_node(node_id, **attrs)

    for link in data.get("links", []):
        source = link.get("source")
        target = link.get("target")

        if source and target:
            attrs = dict(link)
            attrs.pop("source", None)
            attrs.pop("target", None)
            graph.add_edge(source, target, **attrs)

    return graph


def node_label(graph, node_id):
    return graph.nodes[node_id].get("label", node_id)


def run_graphify_query():
    cmd = [
        sys.executable,
        "-m",
        "graphify",
        "query",
        QUERY,
    ]

    result = subprocess.run(
        cmd,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONHASHSEED": "0"},
    )

    return result


def verify_chain(graph):
    print("\n=== STRUCTURAL GROUND TRUTH ===")

    missing = [node for node in EXPECTED_CHAIN if not graph.has_node(node)]

    if missing:
        print("FAIL: Missing expected nodes:")
        for node in missing:
            print(f"  - {node}")
        return False

    print("All expected chain nodes exist.")

    failures = []

    for source, target in zip(EXPECTED_CHAIN, EXPECTED_CHAIN[1:]):
        if not graph.has_edge(source, target):
            failures.append((source, target))
        else:
            relations = sorted({
                attrs.get("relation")
                for attrs in graph[source][target].values()
            })
            print(
                f"PASS: {node_label(graph, source)}"
                f" -> {node_label(graph, target)}"
                f" [{', '.join(str(r) for r in relations)}]"
            )

    if failures:
        print("\nFAIL: Expected direct relationships missing:")
        for source, target in failures:
            print(f"  - {source} -> {target}")
        return False

    print("Structural 4-tier chain verified.")
    return True


def verify_additional_nodes(graph):
    print("\n=== ADDITIONAL RANKING FUNCTIONS ===")

    ok = True

    for node in EXPECTED_ADDITIONAL:
        if graph.has_node(node):
            print(f"PASS: {node_label(graph, node)} exists")

            parent = EXPECTED_CHAIN[1]

            if graph.has_edge(parent, node):
                print(
                    f"  PASS: rank_document -> "
                    f"{node_label(graph, node)}"
                )
            else:
                print(
                    f"  FAIL: expected rank_document -> "
                    f"{node_label(graph, node)}"
                )
                ok = False
        else:
            print(f"FAIL: Missing {node}")
            ok = False

    return ok


def query_output_contains_expected_symbols(output):
    print("\n=== GRAPHIFY QUERY OUTPUT ===")

    output_lower = output.lower()

    checks = {
        "query_retrieval_api": "query_retrieval_api" in output_lower,
        "rank_document": "rank_document" in output_lower,
        "score_term_matches": "score_term_matches" in output_lower,
        "tokenize": "tokenize" in output_lower,
    }

    for name, found in checks.items():
        print(f"{'PASS' if found else 'MISS'}: {name}")

    return all(checks.values()), checks


def main():
    print("Graphify Retrieval Benchmark")
    print("=" * 60)
    print(f"Workspace : {WORKSPACE}")
    print(f"Graph     : {GRAPH_JSON}")
    print(f"Query     : {QUERY}")

    if not GRAPH_JSON.exists():
        print("\nFAIL: graph.json does not exist.")
        return 1

    graph = load_graph()

    print("\n=== GRAPH METADATA ===")
    print(f"Nodes : {graph.number_of_nodes()}")
    print(f"Edges : {graph.number_of_edges()}")

    ground_truth_ok = verify_chain(graph)
    additional_ok = verify_additional_nodes(graph)

    print("\n=== EXECUTING GRAPHIFY QUERY ===")

    result = run_graphify_query()

    print(f"Return code: {result.returncode}")

    query_output = (result.stdout or "") + (result.stderr or "")

    if query_output:
        print("\n--- Graphify output ---")
        print(query_output)

    query_symbols_ok, symbol_checks = (
        query_output_contains_expected_symbols(query_output)
    )

    print("\n=== OUTPUT SIZE ===")
    print(f"Characters : {len(query_output):,}")
    print(f"Lines      : {len(query_output.splitlines()):,}")
    print(f"Approx KB  : {len(query_output.encode('utf-8')) / 1024:.2f}")

    print("\n=== BENCHMARK RESULT ===")

    if result.returncode != 0:
        print("GRAPHIFY QUERY: FAIL")
    else:
        print("GRAPHIFY QUERY: EXECUTED")

    print(
        "GROUND TRUTH : "
        + ("PASS" if ground_truth_ok else "FAIL")
    )

    print(
        "ADDITIONAL   : "
        + ("PASS" if additional_ok else "FAIL")
    )

    print(
        "QUERY SYMBOLS: "
        + ("PASS" if query_symbols_ok else "PARTIAL/MISS")
    )

    print("\n=== INTERPRETATION ===")

    if ground_truth_ok and result.returncode == 0:
        if query_symbols_ok:
            print(
                "Graphify query surfaced the expected retrieval symbols."
            )
        else:
            print(
                "Graphify query executed, but did not expose all "
                "expected symbols in its textual output."
            )

    print(
        "\nNote: structural correctness is determined from graph.json; "
        "query-output matching is evaluated separately."
    )

    return 0 if ground_truth_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
