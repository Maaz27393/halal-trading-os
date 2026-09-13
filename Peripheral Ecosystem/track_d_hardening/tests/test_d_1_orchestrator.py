import sys
import os

# Point Python path to Peripheral Ecosystem root
PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from track_d_hardening.orchestrator.pipeline import PeripheralOrchestrator

def run_d_1_tests():
    print("=" * 70)
    print("STARTING TRACK D.1 — UNIFIED ORCHESTRATION & HARDENING TESTS")
    print("=" * 70)

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup global permissions
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")
    perm_gateway.grant_permission("risk_analyst", "READ")

    orchestrator = PeripheralOrchestrator(permission_gateway=perm_gateway, role="analyst_agent")

    # 3. Define test payload data
    raw_universe = [
        {"symbol": "RELIANCE", "sector": "Energy", "roe": 16.2, "rsi": 55.0, "volume_spike_ratio": 1.5, "is_compliant": True},
        {"symbol": "INFY", "sector": "IT", "roe": 14.1, "rsi": 48.0, "volume_spike_ratio": 1.3, "is_compliant": True}
    ]
    criteria = {"min_roe": 12.0, "max_rsi": 70.0, "min_volume_spike": 1.2}
    trade_setup = {
        "symbol": "RELIANCE",
        "entry_price": 2500.0,
        "stop_loss": 2450.0,
        "target_price": 2600.0,
        "account_capital": 500000.0,
        "risk_percentage": 1.0
    }

    # 4. Execute full unified pipeline
    result = orchestrator.run_full_pipeline(
        query="Earnings",
        raw_stocks=raw_universe,
        screening_criteria=criteria,
        trade_setup=trade_setup
    )

    assert result.status == "SUCCESS", "Pipeline execution failed!"
    assert len(result.steps_completed) == 5, "Pipeline step count mismatch!"
    assert os.path.exists(result.export_path), "Orchestrated report export not found on disk!"
    assert result.has_execution_payload is False, "Execution safety invariant violated!"
    
    print(f" -> SUCCESS: Unified pipeline executed successfully. Workflow ID: {result.workflow_id}")
    print(f" -> SUCCESS: Steps completed: {result.steps_completed}")
    print(f" -> SUCCESS: Final report exported to: {result.export_path}")

    print("=" * 70)
    print("TRACK D.1 UNIFIED ORCHESTRATION & HARDENING VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_d_1_tests()