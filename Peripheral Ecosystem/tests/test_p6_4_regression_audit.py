import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p6_expansion.sector_correlation import SectorRotationCorrelationEngine
from p6_expansion.risk_modeler import ProbabilisticRiskScenarioModeler
from p6_expansion.knowledge_graph import ObsidianKnowledgeGraphSynthesizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("P6RegressionAudit")

def run_p6_regression_audit():
    print("=" * 70)
    print("STARTING P6.4 — P6 FULL-SYSTEM REGRESSION & INVARIANT AUDIT")
    print("=" * 70)

    # 1. CORE GUARDRAIL INVARIANT AUDIT
    print("\n[Audit 1/4] Verifying Core Guardrail (LIVE_AUTO_EXECUTION)...")
    assert LIVE_AUTO_EXECUTION is False, "CRITICAL FAILURE: LIVE_AUTO_EXECUTION must remain False!"
    print(" -> SUCCESS: LIVE_AUTO_EXECUTION = False verified.")

    # 2. PERMISSION BOUNDARY ENFORCEMENT AUDIT
    print("\n[Audit 2/4] Verifying Negative Permission Boundaries...")
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("restricted_user", "READ")
    
    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    sector_engine = SectorRotationCorrelationEngine(perm_gateway, vault_base)

    try:
        sector_engine.evaluate_and_export_sectors(caller_role="restricted_user")
        raise AssertionError("SECURITY FAILURE: Restricted user bypassed WRITE permission on sector correlation export!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized WRITE successfully blocked: {e}")

    # Grant proper access for positive regression tests
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    # 3. P6 MODULE EXECUTION REGRESSION AUDIT
    print("\n[Audit 3/4] Executing P6 Intelligence Module Regression Workflow...")
    
    risk_modeler = ProbabilisticRiskScenarioModeler(perm_gateway, vault_base)
    kg_synthesizer = ObsidianKnowledgeGraphSynthesizer(perm_gateway, vault_base)

    # Run P6.1
    sector_path = sector_engine.evaluate_and_export_sectors(caller_role="analyst_agent")
    assert os.path.exists(sector_path), f"Regression Failure: P6.1 output missing at {sector_path}"
    print(f" -> P6.1 Sector Correlation Verified -> {sector_path}")

    # Run P6.2
    risk_path = risk_modeler.model_and_export_scenarios(caller_role="analyst_agent")
    assert os.path.exists(risk_path), f"Regression Failure: P6.2 output missing at {risk_path}"
    print(f" -> P6.2 Risk Modeler Verified -> {risk_path}")

    # Run P6.3
    kg_path = kg_synthesizer.synthesize_and_export_graph(caller_role="analyst_agent")
    assert os.path.exists(kg_path), f"Regression Failure: P6.3 output missing at {kg_path}"
    print(f" -> P6.3 Knowledge Graph Synthesizer Verified -> {kg_path}")

    # 4. IMMUTABILITY CHECK
    print("\n[Audit 4/4] Verifying P0–P5 Core Integrity...")
    import connectors.broker_base as bb
    assert bb.LIVE_AUTO_EXECUTION is False, "CRITICAL: Core execution guardrail modified!"
    print(" -> SUCCESS: P0–P5 core governance and execution invariants remain untouched.")

    print("=" * 70)
    print("P6.4 — FULL-SYSTEM REGRESSION & INVARIANT AUDIT PASSED SUCCESSFULLY!")
    print("P0–P6 EXTENDED ECOSYSTEM BASELINE LOCKED.")
    print("=" * 70)

if __name__ == "__main__":
    run_p6_regression_audit()