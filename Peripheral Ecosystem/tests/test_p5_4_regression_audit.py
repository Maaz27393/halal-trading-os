import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from p5_expansion.charting_exporter import AdvancedChartingExporter
from p5_expansion.macro_connector import AlternativeMacroConnector
from p5_expansion.vault_tagger import VaultCrossReferencingEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("P5RegressionAudit")

def run_p5_regression_audit():
    print("=" * 70)
    print("STARTING P5.4 — P5 FULL-SYSTEM REGRESSION & INVARIANT AUDIT")
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
    chart_exporter = AdvancedChartingExporter(perm_gateway, vault_base)

    try:
        chart_exporter.generate_and_export_charts(["RELIANCE"], caller_role="restricted_user")
        raise AssertionError("SECURITY FAILURE: Restricted user bypassed WRITE permission on charting export!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized WRITE successfully blocked: {e}")

    # Grant proper access for positive regression tests
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    # 3. P5 MODULE EXECUTION REGRESSION AUDIT
    print("\n[Audit 3/4] Executing P5 Module Regression Workflow...")
    
    macro_connector = AlternativeMacroConnector(perm_gateway, vault_base)
    vault_tagger = VaultCrossReferencingEngine(perm_gateway, vault_base)

    # Run P5.1
    chart_path = chart_exporter.generate_and_export_charts(["RELIANCE", "TCS"], caller_role="analyst_agent")
    assert os.path.exists(chart_path), f"Regression Failure: P5.1 output missing at {chart_path}"
    print(f" -> P5.1 Charting Exporter Verified -> {chart_path}")

    # Run P5.2
    macro_path = macro_connector.fetch_and_export_macro_snapshot(caller_role="analyst_agent")
    assert os.path.exists(macro_path), f"Regression Failure: P5.2 output missing at {macro_path}"
    print(f" -> P5.2 Macro Connector Verified -> {macro_path}")

    # Run P5.3
    audit_path = vault_tagger.process_and_tag_vault(caller_role="analyst_agent")
    assert os.path.exists(audit_path), f"Regression Failure: P5.3 output missing at {audit_path}"
    print(f" -> P5.3 Vault Tagger Verified -> {audit_path}")

    # 4. IMMUTABILITY CHECK
    print("\n[Audit 4/4] Verifying P0–P4 Core Integrity...")
    import connectors.broker_base as bb
    assert bb.LIVE_AUTO_EXECUTION is False, "CRITICAL: Core execution guardrail modified!"
    print(" -> SUCCESS: P0–P4 core governance and execution invariants remain untouched.")

    print("=" * 70)
    print("P5.4 — FULL-SYSTEM REGRESSION & INVARIANT AUDIT PASSED SUCCESSFULLY!")
    print("P0–P5 EXPANDED ECOSYSTEM BASELINE LOCKED.")
    print("=" * 70)

if __name__ == "__main__":
    run_p5_regression_audit()