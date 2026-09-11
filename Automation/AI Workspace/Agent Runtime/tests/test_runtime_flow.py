import sys
import json
from pathlib import Path

runtime_path = Path(__file__).parent.parent
sys.path.append(str(runtime_path))

from runtime import AgentRuntime

def run_runtime_benchmark():
    agent = AgentRuntime()
    test_cases = [
        {
            "name": "L0 Governance Protection Test",
            "query": "What are the mandatory risk limits and capital rules?",
            "kwargs": {"proposed_risk_pct": 0.5, "positions_today": 0, "is_cash_trade": True},
            "expected_intent": "RULE_LOOKUP",
            "expected_rank": 1
        },
        {
            "name": "Rule Compliance Violation Test",
            "query": "Can I open a trade with 2.5% risk on margin?",
            "kwargs": {"proposed_risk_pct": 2.5, "positions_today": 0, "is_cash_trade": False},
            "expected_intent": "TRADE_PRECHECK",
            "expected_rank": 1
        },
        {
            "name": "Journal Analysis L3 Isolation Test",
            "query": "Analyze my recent trading journal mistakes",
            "kwargs": {},
            "expected_intent": "JOURNAL_ANALYSIS",
            "expected_rank": 4
        }
    ]

    passed = 0
    total = len(test_cases)

    print("=== STARTING PHASE 5B RUNTIME BENCHMARK ===")
    for i, test in enumerate(test_cases, 1):
        res = agent.process_query(test["query"], test["kwargs"])
        intent_match = res["intent"] == test["expected_intent"]
        rank_match = res["max_authority_rank"] == test["expected_rank"]
        status_ok = res["status"] in ["SUCCESS", "BLOCKED"]

        if intent_match and rank_match and status_ok:
            print(f"[PASS] Test {i}: {test['name']}")
            print(f"       Routed Intent: {res['intent']} | Rank: {res['max_authority_rank']}")
            passed += 1
        else:
            print(f"[FAIL] Test {i}: {test['name']}")
            print(f"       Expected Intent: {test['expected_intent']}, Got: {res['intent']}")

    print(f"\nBenchmark Result: {passed}/{total} Passed")
    return passed == total

if __name__ == "__main__":
    success = run_runtime_benchmark()
    sys.exit(0 if success else 1)
