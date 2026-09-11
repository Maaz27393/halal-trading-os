import sys
from pathlib import Path
from typing import Dict, Any

workspace_path = Path(__file__).parent.parent
runtime_path = workspace_path / "Agent Runtime"
sys.path.extend([
    str(Path(__file__).parent),
    str(runtime_path),
    str(runtime_path / "skills")
])

from rule_verification_suite import RuleVerificationSuite
from strategy_analysis_suite import StrategyAnalysisSuite
from trade_precheck_suite import TradePrecheckSuite
from governance_check_suite import GovernanceCheckSuite
from sop_execution_assistant import SOPExecutionAssistant

class OrchestratorRouter:
    """
    Central Orchestrator Dispatch Router
    Maps task intents to dedicated Phase 7 Skill Modules.
    """
    def __init__(self):
        self.skills = {
            "RULE_VERIFICATION": RuleVerificationSuite(),
            "STRATEGY_ANALYSIS": StrategyAnalysisSuite(),
            "TRADE_PRECHECK": TradePrecheckSuite(),
            "GOVERNANCE_CHECK": GovernanceCheckSuite(),
            "SOP_EXECUTION": SOPExecutionAssistant()
        }

    def route_and_execute(self, intent: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        skill = self.skills.get(intent)
        if not skill:
            return {
                "status": "ERROR",
                "message": f"Unknown intent '{intent}'. Valid intents: {list(self.skills.keys())}"
            }
        
        result = skill.execute(payload)
        return {
            "status": "SUCCESS",
            "intent": intent,
            "result": result
        }
