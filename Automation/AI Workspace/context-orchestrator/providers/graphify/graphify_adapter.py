from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Set

from contracts.context_contracts import ContextRequest, ProviderResult
from providers.base_provider import ContextProvider


class GraphifyProvider(ContextProvider):
    """
    Read-only adapter for the local Graphify graph artifact.

    The adapter performs deterministic structural lookup over the existing
    graph JSON. It does not modify or rebuild the graph.
    """

    name = "graphify"

    def __init__(self, graph_path: str | Path):
        self.graph_path = Path(graph_path)

    def capabilities(self) -> List[str]:
        return [
            "ast_graph",
            "symbol_lookup",
            "dependency_lookup",
            "structural_context",
        ]

    def health(self) -> bool:
        return self.graph_path.exists() and self.graph_path.is_file()

    def _load_graph(self) -> Dict[str, Any]:
        with self.graph_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _node_text(node: Dict[str, Any]) -> str:
        fields = [
            node.get("id"),
            node.get("name"),
            node.get("symbol"),
            node.get("qualified_name"),
            node.get("path"),
            node.get("file"),
            node.get("type"),
            node.get("node_type"),
        ]

        return " ".join(
            str(value)
            for value in fields
            if value is not None
        ).lower()

    @staticmethod
    def _edge_values(edge: Dict[str, Any]) -> tuple[str | None, str | None]:
        source = (
            edge.get("source")
            or edge.get("from")
            or edge.get("src")
        )

        target = (
            edge.get("target")
            or edge.get("to")
            or edge.get("dst")
        )

        return (
            str(source) if source is not None else None,
            str(target) if target is not None else None,
        )

    def retrieve(self, request: ContextRequest) -> ProviderResult:
        if not self.graph_path.exists():
            return ProviderResult(
                provider=self.name,
                status="UNAVAILABLE",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "graphify_graph",
                    "path": str(self.graph_path),
                },
                errors=[f"Graph file not found: {self.graph_path}"],
            )

        try:
            graph = self._load_graph()
        except (OSError, json.JSONDecodeError) as exc:
            return ProviderResult(
                provider=self.name,
                status="ERROR",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "graphify_graph",
                    "path": str(self.graph_path),
                },
                errors=[str(exc)],
            )

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        if not isinstance(nodes, list):
            nodes = []

        if not isinstance(edges, list):
            edges = []

        query_terms = {
            term.strip().lower()
            for term in request.user_query.replace("/", " ").split()
            if term.strip()
        }

        requested_symbols = {
            symbol.strip().lower()
            for symbol in request.required_symbols
            if symbol.strip()
        }

        matched_nodes: List[Dict[str, Any]] = []

        for node in nodes:
            if not isinstance(node, dict):
                continue

            text = self._node_text(node)

            explicit_match = any(
                symbol in text
                for symbol in requested_symbols
            )

            query_match = any(
                term in text
                for term in query_terms
                if len(term) >= 3
            )

            if explicit_match or query_match:
                matched_nodes.append(node)

        matched_ids: Set[str] = set()

        for node in matched_nodes:
            node_id = (
                node.get("id")
                or node.get("name")
                or node.get("symbol")
            )

            if node_id is not None:
                matched_ids.add(str(node_id))

        related_edges: List[Dict[str, Any]] = []

        for edge in edges:
            if not isinstance(edge, dict):
                continue

            source, target = self._edge_values(edge)

            if source in matched_ids or target in matched_ids:
                related_edges.append(edge)

        result = {
            "query": request.user_query,
            "matched_symbols": [
                node.get("name")
                or node.get("symbol")
                or node.get("qualified_name")
                or node.get("id")
                for node in matched_nodes
            ],
            "nodes": matched_nodes,
            "edges": related_edges,
            "graph_statistics": {
                "nodes_total": len(nodes),
                "edges_total": len(edges),
                "matched_nodes": len(matched_nodes),
                "related_edges": len(related_edges),
            },
        }

        return ProviderResult(
            provider=self.name,
            status="SUCCESS",
            query=request.user_query,
            content=result,
            provenance={
                "source_type": "graphify_graph",
                "path": str(self.graph_path),
                "read_only": True,
            },
            metadata={
                "nodes_total": len(nodes),
                "edges_total": len(edges),
            },
        )
