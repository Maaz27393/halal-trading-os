from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict

class IntentCategory(str, Enum):
    RULE_LOOKUP = "RULE_LOOKUP"
    STRATEGY_LOOKUP = "STRATEGY_LOOKUP"
    SOP_LOOKUP = "SOP_LOOKUP"
    GOVERNANCE_CHECK = "GOVERNANCE_CHECK"
    CONFLICT_CHECK = "CONFLICT_CHECK"
    TRADE_PRECHECK = "TRADE_PRECHECK"
    JOURNAL_ANALYSIS = "JOURNAL_ANALYSIS"
    RESEARCH_QUERY = "RESEARCH_QUERY"
    GENERAL_KNOWLEDGE = "GENERAL_KNOWLEDGE"
    UNKNOWN = "UNKNOWN"

@dataclass
class IntentConfig:
    category: IntentCategory
    description: str
    allowed_layers: List[str]
    permitted_tools: List[str]
    max_authority_rank: int  # Lowest numerical rank permitted (1 is highest authority)

INTENT_PERMISSIONS: Dict[IntentCategory, IntentConfig] = {
    IntentCategory.RULE_LOOKUP: IntentConfig(
        category=IntentCategory.RULE_LOOKUP,
        description="Query regarding mandatory trading rules, capital limits, or risk parameters.",
        allowed_layers=["L0_SYSTEM", "L1_KNOWLEDGE"],
        permitted_tools=["vault_search"],
        max_authority_rank=1
    ),
    IntentCategory.STRATEGY_LOOKUP: IntentConfig(
        category=IntentCategory.STRATEGY_LOOKUP,
        description="Query regarding active trading strategy rules (Pullback, Breakout).",
        allowed_layers=["L0_SYSTEM", "L1_KNOWLEDGE"],
        permitted_tools=["vault_search"],
        max_authority_rank=2
    ),
    IntentCategory.SOP_LOOKUP: IntentConfig(
        category=IntentCategory.SOP_LOOKUP,
        description="Lookup of standard operating procedures and workflows.",
        allowed_layers=["L1_KNOWLEDGE"],
        permitted_tools=["vault_search"],
        max_authority_rank=2
    ),
    IntentCategory.GOVERNANCE_CHECK: IntentConfig(
        category=IntentCategory.GOVERNANCE_CHECK,
        description="Verification against Decision Log entries and rule updates.",
        allowed_layers=["L0_SYSTEM"],
        permitted_tools=["vault_search"],
        max_authority_rank=1
    ),
    IntentCategory.CONFLICT_CHECK: IntentConfig(
        category=IntentCategory.CONFLICT_CHECK,
        description="Cross-referencing rules or strategies for internal contradictions.",
        allowed_layers=["L0_SYSTEM", "L1_KNOWLEDGE"],
        permitted_tools=["vault_search"],
        max_authority_rank=2
    ),
    IntentCategory.TRADE_PRECHECK: IntentConfig(
        category=IntentCategory.TRADE_PRECHECK,
        description="Pre-execution compliance validation for a planned trade setup.",
        allowed_layers=["L0_SYSTEM", "L1_KNOWLEDGE", "L2_SESSION"],
        permitted_tools=["vault_search"],
        max_authority_rank=1
    ),
    IntentCategory.JOURNAL_ANALYSIS: IntentConfig(
        category=IntentCategory.JOURNAL_ANALYSIS,
        description="Evaluating historical trades, trade logs, and execution lessons.",
        allowed_layers=["L1_KNOWLEDGE", "L2_SESSION", "L3_PERSISTENT"],
        permitted_tools=["vault_search"],
        max_authority_rank=4
    ),
    IntentCategory.RESEARCH_QUERY: IntentConfig(
        category=IntentCategory.RESEARCH_QUERY,
        description="General research, market concepts, or technical analysis indicators.",
        allowed_layers=["L1_KNOWLEDGE"],
        permitted_tools=["vault_search"],
        max_authority_rank=2
    ),
    IntentCategory.GENERAL_KNOWLEDGE: IntentConfig(
        category=IntentCategory.GENERAL_KNOWLEDGE,
        description="Conversational or non-trading vault queries.",
        allowed_layers=["L2_SESSION", "L3_PERSISTENT"],
        permitted_tools=[],
        max_authority_rank=4
    ),
    IntentCategory.UNKNOWN: IntentConfig(
        category=IntentCategory.UNKNOWN,
        description="Ambiguous or unclassified query.",
        allowed_layers=["L2_SESSION"],
        permitted_tools=[],
        max_authority_rank=4
    )
}
