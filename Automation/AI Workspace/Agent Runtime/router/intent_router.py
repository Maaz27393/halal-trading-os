import json
from pathlib import Path
from typing import Dict, Any
from intent_schemas import IntentCategory, INTENT_PERMISSIONS, IntentConfig

class IntentRouter:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "authority_rules.json"
        
        with open(config_path, "r", encoding="utf-8-sig") as f:
            self.authority_rules = json.load(f)

    def route_query(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        
        # Explicit action execution prompts take highest precedence
        if any(k in q for k in ["can i open", "can i trade", "can i buy", "entry check", "precheck", "can i "]):
            category = IntentCategory.TRADE_PRECHECK
        elif any(k in q for k in ["decision log", "governance", "amendment", "proposal"]):
            category = IntentCategory.GOVERNANCE_CHECK
        elif any(k in q for k in ["pullback", "breakout", "strategy", "ema"]):
            category = IntentCategory.STRATEGY_LOOKUP
        elif any(k in q for k in ["sop", "workflow", "checklist"]):
            category = IntentCategory.SOP_LOOKUP
        elif any(k in q for k in ["journal", "lesson", "past trade", "mistake"]):
            category = IntentCategory.JOURNAL_ANALYSIS
        elif any(k in q for k in ["conflict", "contradiction", "mismatch"]):
            category = IntentCategory.CONFLICT_CHECK
        elif any(k in q for k in ["rule", "risk", "capital limit", "max position", "leverage", "cash-only"]):
            category = IntentCategory.RULE_LOOKUP
        elif any(k in q for k in ["trade", "buy", "entry", "stop loss"]):
            category = IntentCategory.TRADE_PRECHECK
        elif any(k in q for k in ["indicator", "rsi", "vwap", "volume"]):
            category = IntentCategory.RESEARCH_QUERY
        else:
            category = IntentCategory.UNKNOWN

        config: IntentConfig = INTENT_PERMISSIONS[category]

        return {
            "query": query,
            "intent": category.value,
            "allowed_layers": config.allowed_layers,
            "permitted_tools": config.permitted_tools,
            "max_authority_rank": config.max_authority_rank,
            "description": config.description
        }

if __name__ == "__main__":
    router = IntentRouter()
    sample = "Explain the entry criteria for the EMA20-50 Pullback strategy."
    print(json.dumps(router.route_query(sample), indent=2))
