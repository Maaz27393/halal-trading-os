from pathlib import Path
import ast
import json
import os
import re
import sys


# ============================================================
# RETRIEVAL CONFIGURATION
# ============================================================

DEFAULT_VAULT_ROOT = Path(
    r"D:\OBSIDIAN VAULT\halal-trading-os"
)

VAULT_ROOT = Path(
    os.getenv(
        "HALAL_TRADING_VAULT",
        str(DEFAULT_VAULT_ROOT)
    )
)

MAX_RESULTS = 10
SNIPPET_LINES = 12
API_VERSION = "1.0"


# ============================================================
# AUTHORITY WEIGHTS
# ============================================================

AUTHORITY_WEIGHTS = {
    "decision": 100,
    "system_rule": 100,
    "strategy": 75,
    "sop": 60,
    "research": 40,
    "knowledge": 30,
    "template": 10,
    "trading_os": 10,
    "unknown": 0,
}


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "can",
    "contains",
    "current",
    "do",
    "does",
    "for",
    "from",
    "has",
    "have",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "my",
    "new",
    "of",
    "on",
    "or",
    "should",
    "the",
    "their",
    "this",
    "to",
    "what",
    "when",
    "which",
    "who",
    "with",
}


# ============================================================
# TOPIC GROUPS
# ============================================================

TOPIC_GROUPS = {
    "ema20": {
        "ema20",
        "ema 20",
    },
    "ema20-50": {
        "ema20-50",
        "ema20 50",
        "ema 20 50",
        "ema20/50",
        "ema 20/50",
    },
    "pullback": {
        "pullback",
        "pull back",
    },
    "breakout": {
        "breakout",
        "break out",
    },
    "vwap": {
        "vwap",
        "volume weighted average price",
    },
    "volume": {
        "volume",
        "volume profile",
    },
    "rsi": {
        "rsi",
        "relative strength index",
    },
    "atr": {
        "atr",
        "average true range",
    },
    "pivot": {
        "pivot",
        "pivot point",
        "pivot points",
    },
    "market breadth": {
        "market breadth",
        "advance decline",
        "advance/decline",
    },
    "india vix": {
        "india vix",
        "vix",
    },
    "halal": {
        "halal",
        "shariah",
        "sharia",
    },
    "risk": {
        "risk",
        "risk management",
        "position sizing",
        "position size",
    },
    "entry": {
        "entry",
        "entry condition",
        "entry conditions",
    },
    "exit": {
        "exit",
        "exit condition",
        "exit conditions",
    },
}


# ============================================================
# FRONTMATTER PARSING
# ============================================================

def _parse_yaml_value(value):
    value = value.strip()

    if not value:
        return ""

    # Quoted scalar
    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {"'", '"'}
    ):
        return value[1:-1]

    # Inline list
    if value.startswith("[") and value.endswith("]"):
        try:
            return ast.literal_eval(value)
        except Exception:
            inner = value[1:-1].strip()

            if not inner:
                return []

            return [
                item.strip().strip("'\"")
                for item in inner.split(",")
                if item.strip()
            ]

    # Boolean
    lowered = value.lower()

    if lowered == "true":
        return True

    if lowered == "false":
        return False

    if lowered in {"null", "none"}:
        return None

    # Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Float
    try:
        return float(value)
    except ValueError:
        pass

    return value


def extract_frontmatter(text):
    metadata = {}

    lines = text.splitlines()

    if not lines:
        return metadata

    if lines[0].strip() != "---":
        return metadata

    end_index = None

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return metadata

    i = 1

    while i < end_index:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        if ":" not in line:
            i += 1
            continue

        key, raw_value = line.split(":", 1)

        key = key.strip()
        raw_value = raw_value.strip()

        # Block YAML list
        if not raw_value:
            items = []
            j = i + 1

            while j < end_index:
                next_line = lines[j]

                if not next_line.strip():
                    j += 1
                    continue

                stripped = next_line.strip()

                if stripped.startswith("- "):
                    items.append(
                        _parse_yaml_value(
                            stripped[2:].strip()
                        )
                    )
                    j += 1
                    continue

                if (
                    next_line.startswith(" ")
                    or next_line.startswith("\t")
                ):
                    j += 1
                    continue

                break

            if items:
                metadata[key] = items
                i = j
                continue

            metadata[key] = ""
            i += 1
            continue

        metadata[key] = _parse_yaml_value(raw_value)
        i += 1

    return metadata


# ============================================================
# PATH / DOCUMENT TYPE HELPERS
# ============================================================

def normalize_path(path):
    return str(path).replace("\\", "/").lower()


def is_template_path(path):
    return "/templates/" in normalize_path(path)


def is_trading_os_path(path):
    normalized = normalize_path(path)

    return (
        "/trading system/trading os" in normalized
        or normalized.endswith(
            "/trading system/trading os.md.md"
        )
        or normalized.endswith(
            "/trading system/trading os.md"
        )
    )


def detect_document_type(path, metadata):
    """
    Determine document type.

    Templates are always treated as templates.

    Trading OS is explicitly recognized by path/name because
    its frontmatter may not always be perfectly normalized.
    """

    if is_template_path(path):
        return "template"

    if is_trading_os_path(path):
        return "trading_os"

    doc_type = metadata.get("type")

    if isinstance(doc_type, list):
        if doc_type:
            doc_type = doc_type[0]
        else:
            doc_type = None

    if isinstance(doc_type, str):
        doc_type = doc_type.strip().lower()

        if doc_type:
            return doc_type

    return "unknown"


def get_document_status(metadata):
    status = metadata.get("status", "")

    if isinstance(status, list):
        if status:
            status = status[0]
        else:
            status = ""

    return str(status).strip().lower()


def is_active_system_rule(document):
    if is_template_path(document["path"]):
        return False

    return (
        document["type"] == "system_rule"
        and get_document_status(
            document["metadata"]
        ) == "active"
    )


def is_active_strategy(document):
    if is_template_path(document["path"]):
        return False

    return (
        document["type"] == "strategy"
        and get_document_status(
            document["metadata"]
        ) == "active"
    )


def is_research_item(document):
    if is_template_path(document["path"]):
        return False

    return document["type"] == "research"


def is_decision_required(document):
    if is_template_path(document["path"]):
        return False

    text = document["text"].lower()

    phrases = {
        "decision required",
        "decision needed",
        "requires decision",
        "approval required",
        "requires approval",
    }

    return any(
        phrase in text
        for phrase in phrases
    )


def is_actual_conflict(document):
    if is_template_path(document["path"]):
        return False

    text = document["text"].lower()

    conflict_phrases = {
        "actual conflict",
        "conflict exists",
        "conflicting documents",
        "conflicting rules",
        "conflicts with",
        "conflict between",
        "documents disagree",
        "trading documents disagree",
    }

    return any(
        phrase in text
        for phrase in conflict_phrases
    )


# ============================================================
# EVIDENCE CLASSIFICATION
# ============================================================

def classify_evidence(document):
    """
    Evidence hierarchy:

    1. ACTUAL CONFLICT
    2. DECISION REQUIRED
    3. FINAL DECISION AUTHORITY
    4. CHANGE CONTROL / GOVERNANCE
    5. ACTIVE RULE
    6. STRATEGY
    7. RESEARCH ITEM
    8. SUPPORTING DOCUMENT
    """

    if is_template_path(document["path"]):
        return "TEMPLATE"

    if is_actual_conflict(document):
        return "ACTUAL CONFLICT"

    if is_decision_required(document):
        return "DECISION REQUIRED"

    if document["type"] == "decision":
        return "FINAL DECISION AUTHORITY"

    if document["type"] == "trading_os":
        return "CHANGE CONTROL / GOVERNANCE"

    if is_active_system_rule(document):
        return "ACTIVE RULE"

    if is_active_strategy(document):
        return "STRATEGY"

    if is_research_item(document):
        return "RESEARCH ITEM"

    return "SUPPORTING DOCUMENT"


# ============================================================
# NORMALIZATION / TOKENIZATION
# ============================================================

def normalize_text(text):
    text = str(text).lower()

    text = text.replace(
        "–",
        "-"
    ).replace(
        "—",
        "-"
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def tokenize(text):
    normalized = normalize_text(text)

    tokens = re.findall(
        r"[a-z0-9]+(?:[-/][a-z0-9]+)*",
        normalized
    )

    return [
        token
        for token in tokens
        if token not in STOP_WORDS
    ]


# ============================================================
# TOPIC DETECTION
# ============================================================

def detect_topics(text):
    normalized = normalize_text(text)

    topics = []

    for topic, terms in TOPIC_GROUPS.items():
        for term in terms:
            if term in normalized:
                topics.append(topic)
                break

    return topics


def detect_document_topics(document):
    return detect_topics(
        document["text"]
    )


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(query):
    normalized = normalize_text(query)

    # --------------------------------------------------------
    # Conflict intent
    # --------------------------------------------------------

    conflict_terms = {
        "conflict",
        "conflicting",
        "conflicts",
        "disagree",
        "disagreement",
        "documents disagree",
        "trading documents disagree",
        "different instructions",
        "give different instructions",
        "different instruction",
        "final decision",
        "final authority",
        "which document has final",
        "which document contains the final",
        "source of truth",
    }

    if any(
        term in normalized
        for term in conflict_terms
    ):
        return "conflict"

    # --------------------------------------------------------
    # Change-control / governance intent
    # --------------------------------------------------------

    change_control_terms = {
        "approval",
        "approve",
        "approved",
        "requires approval",
        "approval before",
        "decision before",
        "decision required before",
        "decision needed before",
        "before active",
        "before becoming active",
        "new rule",
        "rule change",
        "activate rule",
        "activate",
        "promote to active",
        "promote into active",
        "promote to trading os",
        "promote into trading os",
        "update trading os",
        "trading os update",
        "trading os updates",
        "change control",
        "change-control",
        "governance",
        "workflow for changing",
        "workflow for activating",
        "process for changing",
        "process for activating",
        "research to decision",
        "evidence to decision",
        "decision to trading os",
        "research promotion",
        "research promotion process",
        "promoting research",
        "promote research",
        "promotion of research",
        "research into an active",
        "research into active",
        "research to an active rule",
        "research into a trading os rule",
        "research into trading os",
        "promote a research",
        "promote research into",
        "research to active rule",
        "research to active",
        "become an active rule",
        "become a trading os rule",
        "promoted into an active",
        "promoted to an active",
        "active trading os rule",
        "who decides",
        "who decides whether",
        "proposed rule",
        "should become active",
    }

    if any(
        term in normalized
        for term in change_control_terms
    ):
        return "change_control"

    # Research + promotion/activation combination
    research_present = (
        "research" in normalized
    )

    promotion_present = any(
        term in normalized
        for term in {
            "promotion",
            "promote",
            "promoting",
            "promoted",
            "activation",
            "activate",
            "active",
            "become",
        }
    )

    rule_present = any(
        term in normalized
        for term in {
            "rule",
            "rules",
            "trading os",
        }
    )

    if (
        research_present
        and promotion_present
        and rule_present
    ):
        return "change_control"

    # --------------------------------------------------------
    # Research intent
    # --------------------------------------------------------

    research_terms = {
        "research",
        "study",
        "evidence",
        "finding",
        "findings",
        "hypothesis",
        "research finding",
        "research findings",
    }

    if any(
        term in normalized
        for term in research_terms
    ):
        return "research"

    # --------------------------------------------------------
    # Decision intent
    # --------------------------------------------------------

    decision_terms = {
        "decision",
        "decisions",
        "decision log",
        "what was decided",
        "decided",
        "decision authority",
    }

    if any(
        term in normalized
        for term in decision_terms
    ):
        return "decision"

    # --------------------------------------------------------
    # Strategy intent
    # --------------------------------------------------------

    strategy_terms = {
        "strategy",
        "setup",
        "setup conditions",
        "entry conditions",
        "pullback strategy",
        "breakout strategy",
        "conditions define",
        "conditions define the",
    }

    if any(
        term in normalized
        for term in strategy_terms
    ):
        return "strategy"

    # --------------------------------------------------------
    # Rules intent
    # --------------------------------------------------------

    rules_terms = {
        "rules",
        "rule",
        "current rules",
        "active rules",
        "trading rules",
        "entry rules",
        "exit rules",
    }

    if any(
        term in normalized
        for term in rules_terms
    ):
        return "rules"

    return "general"


# ============================================================
# DOCUMENT LOADING
# ============================================================

def load_documents():
    documents = []

    diagnostics = {
        "files_seen": 0,
        "files_loaded": 0,
        "files_skipped": 0,
        "skipped_files": [],
    }

    if not VAULT_ROOT.exists():
        return documents, diagnostics

    for path in VAULT_ROOT.rglob("*.md"):
        diagnostics["files_seen"] += 1

        try:
            text = path.read_text(
                encoding="utf-8"
            )

            metadata = extract_frontmatter(
                text
            )

            relative_path = path.relative_to(
                VAULT_ROOT
            )

            document = {
                "path": relative_path,
                "absolute_path": path,
                "title": path.stem,
                "text": text,
                "metadata": metadata,
            }

            document["type"] = detect_document_type(
                relative_path,
                metadata
            )

            # Trading OS is explicitly normalized.
            if is_trading_os_path(relative_path):
                document["type"] = "trading_os"

            document["status"] = get_document_status(
                metadata
            )

            document["topics"] = detect_document_topics(
                document
            )

            document["evidence"] = classify_evidence(
                document
            )

            documents.append(document)

            diagnostics["files_loaded"] += 1

        except Exception as exc:
            diagnostics["files_skipped"] += 1

            diagnostics["skipped_files"].append({
                "path": str(
                    path.relative_to(VAULT_ROOT)
                ),
                "error": str(exc),
            })

    return documents, diagnostics


# ============================================================
# SCORING
# ============================================================

def score_term_matches(
    query,
    document_text
):
    query_tokens = tokenize(query)
    normalized_document = normalize_text(
        document_text
    )

    exact = 0
    partial = 0

    for token in query_tokens:
        if token in normalized_document:
            exact += 1

        elif any(
            token in word
            for word in re.findall(
                r"[a-z0-9-]+",
                normalized_document
            )
        ):
            partial += 1

    return exact, partial


def score_phrase_matches(
    query,
    document_text
):
    normalized_query = normalize_text(
        query
    )

    normalized_document = normalize_text(
        document_text
    )

    if (
        len(normalized_query) >= 8
        and normalized_query in normalized_document
    ):
        return 1

    return 0


def intent_score(
    document,
    intent
):
    evidence = document["evidence"]

    score = 0

    if intent == "conflict":

        if evidence == "FINAL DECISION AUTHORITY":
            score += 55

        elif evidence == "CHANGE CONTROL / GOVERNANCE":
            score += 35

    elif intent == "decision":

        if evidence == "FINAL DECISION AUTHORITY":
            score += 70

        elif evidence == "CHANGE CONTROL / GOVERNANCE":
            score += 35

    elif intent == "change_control":

        if evidence == "FINAL DECISION AUTHORITY":
            score += 100

        elif evidence == "CHANGE CONTROL / GOVERNANCE":
            score += 90

        elif evidence == "DECISION REQUIRED":
            score += 70

        elif evidence == "ACTIVE RULE":
            score += 20

        elif evidence == "STRATEGY":
            score += 15

        elif evidence == "RESEARCH ITEM":
            score += 15

        elif evidence == "TEMPLATE":
            score -= 100

    elif intent == "strategy":

        if evidence == "STRATEGY":
            score += 40

        elif evidence == "ACTIVE RULE":
            score += 25

    elif intent == "rules":

        if evidence == "ACTIVE RULE":
            score += 40

        elif evidence == "STRATEGY":
            score += 20

    elif intent == "research":

        if evidence == "RESEARCH ITEM":
            score += 40

    return score


def rank_document(
    document,
    query,
    intent,
    query_topics
):
    exact_terms, partial_terms = (
        score_term_matches(
            query,
            document["text"]
        )
    )

    phrase = score_phrase_matches(
        query,
        document["text"]
    )

    document_topics = set(
        document.get("topics", [])
    )

    topic_matches = len(
        document_topics.intersection(
            query_topics
        )
    )

    # --------------------------------------------------------
    # Scoring rationale
    #
    # Phrase match:
    #   +30
    #
    # Exact term:
    #   +2 per matching query token
    #
    # Partial term:
    #   +1 per partial matching token
    #
    # Topic:
    #   +35 per matching topic
    #
    # Authority:
    #   Based on document type
    #
    # Intent:
    #   Intent-specific authority boosts
    #
    # Status:
    #   Active rules/strategies receive additional relevance
    # --------------------------------------------------------

    score = 0

    if phrase > 0:
        score += 30

    score += exact_terms * 2
    score += partial_terms

    score += topic_matches * 35

    score += AUTHORITY_WEIGHTS.get(
        document["type"],
        0
    )

    score += intent_score(
        document,
        intent
    )

    if document["status"] == "active":
        score += 10

    result = {
        "title": document["title"],
        "path": str(document["path"]),
        "type": document["type"],
        "status": document["status"],
        "evidence": document["evidence"],
        "score": score,
        "relevance": (
            score
            - AUTHORITY_WEIGHTS.get(
                document["type"],
                0
            )
            - intent_score(
                document,
                intent
            )
        ),
        "term": exact_terms,
        "partial": partial_terms,
        "phrase": phrase,
        "topic": topic_matches * 35,
        "_doc": document,
    }

    return result


# ============================================================
# AUTHORITY CANDIDATE DETECTION
# ============================================================

def is_authority_candidate(
    result,
    intent
):
    if intent not in {
        "conflict",
        "decision",
        "change_control",
    }:
        return False

    # Governance hierarchy:
    # 1. ACTUAL CONFLICT
    # 2. DECISION REQUIRED
    # 3. FINAL DECISION AUTHORITY
    # 4. CHANGE CONTROL / GOVERNANCE
    #
    # All four classes must survive lexical zero-relevance
    # filtering for governance-related queries.

    return result["evidence"] in {
        "ACTUAL CONFLICT",
        "DECISION REQUIRED",
        "FINAL DECISION AUTHORITY",
        "CHANGE CONTROL / GOVERNANCE",
    }


# ============================================================
# MATCH QUALITY / CONFIDENCE
# ============================================================

def calculate_match_quality(
    results,
    query,
    intent
):
    if not results:
        return "low"

    top = results[0]

    query_tokens = tokenize(query)

    # For governance queries, any of the four highest-priority
    # evidence classes counts as a strong governance match.

    strong_governance = (
        intent in {
            "conflict",
            "decision",
            "change_control",
        }
        and top["evidence"] in {
            "ACTUAL CONFLICT",
            "DECISION REQUIRED",
            "FINAL DECISION AUTHORITY",
            "CHANGE CONTROL / GOVERNANCE",
        }
    )

    if strong_governance:
        return "high"

    if (
        top["phrase"] > 0
        or top["topic"] >= 35
    ):
        return "high"

    if (
        top["term"]
        >= max(
            2,
            len(query_tokens)
        )
    ):
        return "high"

    if top["relevance"] >= 15:
        return "medium"

    return "low"


def calculate_confidence(
    results,
    query,
    intent
):
    match_quality = calculate_match_quality(
        results,
        query,
        intent
    )

    if not results:
        return 0.0

    if match_quality == "high":
        return 0.90

    if match_quality == "medium":
        return 0.65

    return 0.35


# ============================================================
# SNIPPET EXTRACTION
# ============================================================

def make_snippet(
    document,
    query
):
    lines = document["text"].splitlines()

    query_tokens = tokenize(query)

    if not lines:
        return ""

    best_line = 0
    best_score = 0

    for index, line in enumerate(lines):
        normalized = normalize_text(line)

        line_score = 0

        for token in query_tokens:
            if token in normalized:
                line_score += 1

        if line_score > best_score:
            best_score = line_score
            best_line = index

    start = max(
        0,
        best_line - 2
    )

    end = min(
        len(lines),
        start + SNIPPET_LINES
    )

    snippet_lines = lines[start:end]

    return "\n".join(
        snippet_lines
    ).strip()


# ============================================================
# PUBLIC RESULT SERIALIZATION
# ============================================================

def public_result(result):
    return {
        "title": result["title"],
        "path": result["path"],
        "type": result["type"],
        "status": result["status"],
        "evidence": result["evidence"],
        "score": result["score"],
        "relevance": result["relevance"],
        "term": result["term"],
        "partial": result["partial"],
        "phrase": result["phrase"],
        "topic": result["topic"],
        "snippet": make_snippet(
            result["_doc"],
            result.get(
                "_query",
                ""
            )
        ),
    }


# ============================================================
# STRUCTURED EVIDENCE
# ============================================================

def structured_evidence(results):
    evidence = {
        "ACTUAL CONFLICT": [],
        "DECISION REQUIRED": [],
        "FINAL DECISION AUTHORITY": [],
        "CHANGE CONTROL / GOVERNANCE": [],
        "ACTIVE RULE": [],
        "STRATEGY": [],
        "RESEARCH ITEM": [],
        "SUPPORTING DOCUMENT": [],
        "TEMPLATE": [],
    }

    for result in results:
        category = result["evidence"]

        if category in evidence:
            evidence[category].append({
                "title": result["title"],
                "path": result["path"],
                "score": result["score"],
            })

    return evidence


# ============================================================
# SEARCH API
# ============================================================

def search(
    query,
    max_results=MAX_RESULTS
):
    query = str(query).strip()

    documents, diagnostics = (
        load_documents()
    )

    intent = detect_intent(
        query
    )

    query_topics = set(
        detect_topics(query)
    )

    ranked = []

    for document in documents:
        result = rank_document(
            document,
            query,
            intent,
            query_topics
        )

        result["_query"] = query

        lexical_relevance = (
            result["term"]
            + result["partial"]
            + result["phrase"]
            + (
                1
                if result["topic"] > 0
                else 0
            )
        )

        # ----------------------------------------------------
        # Normal relevance filter.
        #
        # Documents with zero lexical/topic/phrase/intent
        # relevance are normally dropped.
        # ----------------------------------------------------

        if (
            lexical_relevance > 0
            or result["score"]
            > AUTHORITY_WEIGHTS.get(
                document["type"],
                0
            )
            + 10
        ):
            ranked.append(result)

    # --------------------------------------------------------
    # Force inclusion for governance-related intents.
    #
    # This prevents high-priority authority/evidence documents
    # from being silently dropped simply because their text
    # has zero lexical overlap with the user's query.
    # --------------------------------------------------------

    forced = []

    if intent in {
        "conflict",
        "decision",
        "change_control",
    }:
        for document in documents:
            result = rank_document(
                document,
                query,
                intent,
                query_topics
            )

            result["_query"] = query

            if is_authority_candidate(
                result,
                intent
            ):
                forced.append(result)

    # Merge forced candidates without duplicates.
    existing_paths = {
        result["path"]
        for result in ranked
    }

    for result in forced:
        if result["path"] not in existing_paths:
            ranked.append(result)
            existing_paths.add(
                result["path"]
            )

    # --------------------------------------------------------
    # Final ranking
    # --------------------------------------------------------

    ranked.sort(
        key=lambda result: (
            result["score"],
            AUTHORITY_WEIGHTS.get(
                result["type"],
                0
            ),
            result["relevance"],
        ),
        reverse=True,
    )

    # Keep the normal top-N results.
    results = ranked[:max_results]

    # Ensure forced governance evidence is retained even if
    # it falls outside the normal top-N ranking.
    result_paths = {
        result["path"]
        for result in results
    }

    for result in forced:
        if result["path"] not in result_paths:
            results.append(result)
            result_paths.add(
                result["path"]
            )

    # --------------------------------------------------------
    # Match quality / confidence
    # --------------------------------------------------------

    match_quality = calculate_match_quality(
        results,
        query,
        intent
    )

    confidence = calculate_confidence(
        results,
        query,
        intent
    )

    # --------------------------------------------------------
    # Serializable results
    # --------------------------------------------------------

    public_results = []

    for result in results:
        public_results.append(
            public_result(result)
        )

    # --------------------------------------------------------
    # Structured API contract
    #
    # {
    #   "query": "...",
    #   "intent": "...",
    #   "confidence": 0.0,
    #   "structured_evidence": {...},
    #   "results": [...],
    #   "vault_status": {...}
    # }
    # --------------------------------------------------------

    return {
        "api_version": API_VERSION,
        "retrieval_version": "3.6",
        "query": query,
        "intent": intent,
        "topics": sorted(
            query_topics
        ),
        "confidence": confidence,
        "match_quality": match_quality,
        "result_count": len(
            public_results
        ),
        "structured_evidence": (
            structured_evidence(
                results
            )
        ),
        "results": public_results,
        "vault_status": {
            "vault_root": str(
                VAULT_ROOT
            ),
            "files_seen": diagnostics[
                "files_seen"
            ],
            "files_loaded": diagnostics[
                "files_loaded"
            ],
            "files_skipped": diagnostics[
                "files_skipped"
            ],
            "skipped_files": diagnostics[
                "skipped_files"
            ],
        },
    }


# ============================================================
# CLI PRINT WRAPPER
# ============================================================

def print_results(
    payload
):
    print()
    print("=" * 70)
    print("RETRIEVAL V3.6")
    print("=" * 70)

    print(
        f"Query: {payload['query']}"
    )

    print(
        f"Intent: {payload['intent']}"
    )

    print(
        f"Confidence: {payload['confidence']:.2f}"
    )

    print(
        f"Match quality: "
        f"{payload['match_quality']}"
    )

    print(
        f"Topics: "
        f"{', '.join(payload['topics']) or 'None'}"
    )

    print(
        f"Results: "
        f"{payload['result_count']}"
    )

    print()
    print("STRUCTURED EVIDENCE")
    print("-" * 70)

    for category, items in (
        payload[
            "structured_evidence"
        ].items()
    ):
        if not items:
            continue

        print(
            f"\n{category}:"
        )

        for item in items:
            print(
                f"  - {item['title']}"
                f" | {item['path']}"
                f" | score={item['score']}"
            )

    print()
    print("RANKED RESULTS")
    print("-" * 70)

    for index, result in enumerate(
        payload["results"],
        start=1
    ):
        print(
            f"\n{index}. "
            f"{result['title']}"
        )

        print(
            f"   Path: "
            f"{result['path']}"
        )

        print(
            f"   Type: "
            f"{result['type']}"
        )

        print(
            f"   Status: "
            f"{result['status'] or 'unknown'}"
        )

        print(
            f"   Evidence: "
            f"{result['evidence']}"
        )

        print(
            f"   Score: "
            f"{result['score']}"
        )

        print(
            f"   Relevance: "
            f"{result['relevance']}"
        )

        print(
            f"   Term: "
            f"{result['term']}"
            f" | Partial: "
            f"{result['partial']}"
            f" | Phrase: "
            f"{result['phrase']}"
            f" | Topic: "
            f"{result['topic']}"
        )

        if result["snippet"]:
            print()
            print(
                "   Snippet:"
            )

            for line in result[
                "snippet"
            ].splitlines():
                print(
                    f"      {line}"
                )

    print()
    print("VAULT STATUS")
    print("-" * 70)

    vault_status = payload[
        "vault_status"
    ]

    print(
        f"Vault: "
        f"{vault_status['vault_root']}"
    )

    print(
        f"Files seen: "
        f"{vault_status['files_seen']}"
    )

    print(
        f"Files loaded: "
        f"{vault_status['files_loaded']}"
    )

    print(
        f"Files skipped: "
        f"{vault_status['files_skipped']}"
    )

    if vault_status[
        "skipped_files"
    ]:
        print()
        print(
            "Skipped files:"
        )

        for item in vault_status[
            "skipped_files"
        ]:
            print(
                f"  - {item['path']}: "
                f"{item['error']}"
            )

    print()
    print("=" * 70)


# ============================================================
# UNSEEN TESTS
# ============================================================

UNSEEN_TESTS = [
    (
        "Does a researched idea need approval before "
        "it can become an active trading rule?",
        "change_control",
    ),
    (
        "How does a research finding become an approved "
        "Trading OS rule?",
        "change_control",
    ),
    (
        "What steps are required to activate a new rule "
        "in the Trading OS?",
        "change_control",
    ),
    (
        "Can research be added directly to the active "
        "Trading OS rules?",
        "change_control",
    ),
    (
        "Who decides whether a proposed rule should "
        "become active?",
        "change_control",
    ),
    (
        "What happens when two trading documents give "
        "different instructions?",
        "conflict",
    ),
    (
        "Which authority resolves a disagreement between "
        "trading rules?",
        "conflict",
    ),
    (
        "What is the source of truth when documents "
        "conflict?",
        "conflict",
    ),
    (
        "Where is the final decision recorded when "
        "rules disagree?",
        "conflict",
    ),
    (
        "Where can I find the EMA20-50 Pullback setup?",
        "strategy",
    ),
    (
        "What conditions define the EMA20-50 Pullback "
        "entry?",
        "strategy",
    ),
    (
        "What are the active entry rules for trading?",
        "rules",
    ),
    (
        "Which rules are currently active in the system?",
        "rules",
    ),
    (
        "What research has been documented about VWAP?",
        "research",
    ),
    (
        "What evidence exists regarding the VWAP hypothesis?",
        "research",
    ),
]


def run_unseen_tests():
    print()
    print("=" * 70)
    print("UNSEEN INTENT TESTS")
    print("=" * 70)

    passed = 0

    for index, (
        query,
        expected_intent
    ) in enumerate(
        UNSEEN_TESTS,
        start=1
    ):
        actual_intent = detect_intent(
            query
        )

        passed_test = (
            actual_intent
            == expected_intent
        )

        if passed_test:
            passed += 1

        status = (
            "PASS"
            if passed_test
            else "FAIL"
        )

        print()
        print(
            f"Test {index}: {status}"
        )

        print(
            f"  Query: {query}"
        )

        print(
            f"  Expected: "
            f"{expected_intent}"
        )

        print(
            f"  Actual: "
            f"{actual_intent}"
        )

    print()
    print("-" * 70)

    print(
        f"Unseen tests passed: "
        f"{passed}/{len(UNSEEN_TESTS)}"
    )

    print("=" * 70)

    return (
        passed
        == len(UNSEEN_TESTS)
    )


# ============================================================
# MAIN
# ============================================================

def main():
    args = sys.argv[1:]

    if "/tests" in args:
        success = run_unseen_tests()

        sys.exit(
            0
            if success
            else 1
        )

    if "/json" in args:
        args = [
            arg
            for arg in args
            if arg != "/json"
        ]

        query = " ".join(args).strip()

        if not query:
            query = input(
                "Query: "
            ).strip()

        payload = search(
            query
        )

        print(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False
            )
        )

        return

    if args:
        query = " ".join(args).strip()

    else:
        query = input(
            "Query: "
        ).strip()

    if not query:
        print(
            "No query provided."
        )

        return

    payload = search(
        query
    )

    print_results(
        payload
    )


if __name__ == "__main__":
    main()