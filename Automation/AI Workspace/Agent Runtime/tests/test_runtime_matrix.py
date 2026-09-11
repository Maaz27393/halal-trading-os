import sys
import json
from pathlib import Path

runtime_path = Path(__file__).parent.parent
sys.path.append(str(runtime_path))

from runtime import AgentRuntime

def run_adversarial_matrix():
    agent = AgentRuntime()
    
    test_cases = [
        # --- Group 1: Intent Routing & Precedence ---
        {
            "id": "TC-01",
            "name": "Standard Rule Lookup",
            "query": "What is the maximum risk per trade allowed?",
            "kwargs": {},
            "expected_intent": "RULE_LOOKUP",
            "expected_rank": 1,
            "expected_status": "SUCCESS"
        },
        {
            "id": "TC-02",
            "name": "Action Precedence over Rule Keyword",
            "query": "Can I open a trade on SBIN with 0.8% risk?",
            "kwargs": {"proposed_risk_pct": 0.8, "positions_today": 0, "is_cash_trade": True},
            "expected_intent": "TRADE_PRECHECK",
            "expected_rank": 1,
            "expected_status": "SUCCESS"
        },
        {
            "id": "TC-03",
            "name": "Governance & Decision Log Routing",
            "query": "Show me the latest Decision Log amendments on position caps.",
            "kwargs": {},
            "expected_intent": "GOVERNANCE_CHECK",
            "expected_rank": 1,
            "expected_status": "SUCCESS"
        },
        {
            "id": "TC-04",
            "name": "Strategy Lookup Routing",
            "query": "Explain the entry criteria for the EMA20-50 Pullback strategy.",
            "kwargs": {},
            "expected_intent": "STRATEGY_LOOKUP",
            "expected_rank": 2,
            "expected_status": "SUCCESS"
        },
        {
            "id": "TC-05",
            "name": "SOP Workflow Query",
            "query": "What is the checklist for pre-market preparation SOP?",
            "kwargs": {},
            "expected_intent": "SOP_LOOKUP",
            "expected_rank": 2,
            "expected_status": "SUCCESS"
        },
        {
            "id": "TC-06",
            "name": "Journal Analysis Isolation",
            "query": "What mistakes did I make in my past trade journal entries?",
            "kwargs": {},
            "expected_intent": "JOURNAL_ANALYSIS",
            "expected_rank": 4,
            "expected_status": "SUCCESS"
        },
        {
            "id": "TC-07",
            "name": "Conflict Detection Query",
            "query": "Is there a contradiction between the BTST rule and Swing position limits?",
            "kwargs": {},
            "expected_intent": "CONFLICT_CHECK",
            "expected_rank": 2,
            "expected_status": "SUCCESS"
        },
        {
            "id": "TC-08",
            "name": "Indicator Research Query",
            "query": "How is VWAP calculated with volume spikes?",
            "kwargs": {},
            "expected_intent": "RESEARCH_QUERY",
            "expected_rank": 2,
            "expected_status": "SUCCESS"
        },
        {
            "id": "TC-09",
            "name": "Unknown Fallback Query",
            "query": "Tell me a story about blue skies and trading.",
            "kwargs": {},
            "expected_intent": "UNKNOWN",
            "expected_rank": 4,
            "expected_status": "SUCCESS"
        },

        # --- Group 2: Pre-Trade Skill Compliance & Violations ---
        {
            "id": "TC-10",
            "name": "Skill Violation - High Risk Percentage",
            "query": "Entry check for trade with 2.0% risk",
            "kwargs": {"proposed_risk_pct": 2.0, "positions_today": 0, "is_cash_trade": True},
            "expected_intent": "TRADE_PRECHECK",
            "expected_rank": 1,
            "expected_status": "SUCCESS",
            "skill_compliant": False
        },
        {
            "id": "TC-11",
            "name": "Skill Violation - Non-Cash / Margin",
            "query": "Precheck buy order using 2x leverage margin",
            "kwargs": {"proposed_risk_pct": 0.5, "positions_today": 0, "is_cash_trade": False},
            "expected_intent": "TRADE_PRECHECK",
            "expected_rank": 1,
            "expected_status": "SUCCESS",
            "skill_compliant": False
        },
        {
            "id": "TC-12",
            "name": "Skill Violation - Max Daily Positions Exceeded",
            "query": "Can I open a 3rd position today?",
            "kwargs": {"proposed_risk_pct": 0.5, "positions_today": 2, "is_cash_trade": True},
            "expected_intent": "TRADE_PRECHECK",
            "expected_rank": 1,
            "expected_status": "SUCCESS",
            "skill_compliant": False
        },

        # --- Group 3: Tool Firewall & Mutation Interception ---
        {
            "id": "TC-13",
            "name": "Firewall Intercept - Write Mutation",
            "query": "Please update risk rule to 2% per trade in vault",
            "kwargs": {},
            "expected_intent": "RULE_LOOKUP",
            "expected_rank": 1,
            "expected_status": "BLOCKED"
        },
        {
            "id": "TC-14",
            "name": "Firewall Intercept - Delete Mutation",
            "query": "Delete all obsolete SOP rules from the system",
            "kwargs": {},
            "expected_intent": "SOP_LOOKUP",
            "expected_rank": 2,
            "expected_status": "BLOCKED"
        },
        {
            "id": "TC-15",
            "name": "Firewall Intercept - Modify Keyword",
            "query": "Modify the maximum position limit rule",
            "kwargs": {},
            "expected_intent": "RULE_LOOKUP",
            "expected_rank": 1,
            "expected_status": "BLOCKED"
        },
        {
            "id": "TC-16",
            "name": "Tool Restriction - General Query Tool Deny",
            "query": "Hello, what can you do?",
            "kwargs": {},
            "expected_intent": "UNKNOWN",
            "expected_rank": 4,
            "expected_status": "SUCCESS"
        },

        # --- Group 4: Edge Cases ---
        {
            "id": "TC-17",
            "name": "Edge Case - Capitalized Case Mutation",
            "query": "OVERWRITE the maximum capital allocation rules",
            "kwargs": {},
            "expected_intent": "RULE_LOOKUP",
            "expected_rank": 1,
            "expected_status": "BLOCKED"
        },
        {
            "id": "TC-18",
            "name": "Edge Case - Mixed Intent Pre-trade & Rule Lookup",
            "query": "Can I trade if stop loss gives 0.9% risk under current rules?",
            "kwargs": {"proposed_risk_pct": 0.9, "positions_today": 1, "is_cash_trade": True},
            "expected_intent": "TRADE_PRECHECK",
            "expected_rank": 1,
            "expected_status": "SUCCESS",
            "skill_compliant": True
        }
    ]

    passed = 0
    total = len(test_cases)

    print("=== STARTING PHASE 5C EXTENDED ADVERSARIAL BENCHMARK MATRIX ===")
    for test in test_cases:
        res = agent.process_query(test["query"], test["kwargs"])
        
        intent_ok = res["intent"] == test["expected_intent"]
        rank_ok = res["max_authority_rank"] == test["expected_rank"]
        status_ok = res["status"] == test["expected_status"]
        
        skill_ok = True
        if "skill_compliant" in test and res.get("skill_output"):
            skill_ok = (res["skill_output"]["compliant"] == test["skill_compliant"])

        if intent_ok and rank_ok and status_ok and skill_ok:
            print(f"[PASS] {test['id']} | {test['name']}")
            passed += 1
        else:
            print(f"[FAIL] {test['id']} | {test['name']}")
            print(f"       Details: Status={res['status']} (Exp: {test['expected_status']}), Intent={res['intent']} (Exp: {test['expected_intent']}), Rank={res['max_authority_rank']}")
            if not skill_ok:
                print(f"       Skill mismatch: Got {res['skill_output']['compliant']}, Expected {test['skill_compliant']}")

    print(f"\nMatrix Benchmark Result: {passed}/{total} Passed")
    return passed == total

if __name__ == "__main__":
    success = run_adversarial_matrix()
    sys.exit(0 if success else 1)
