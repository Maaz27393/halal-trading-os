import sys
import os

# Point Python path to Peripheral Ecosystem root
PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from track_c_workspace.risk_engine.risk_adapter import C1RiskManagementEngine

def run_c_1_tests():
    print("=" * 70)
    print("STARTING TRACK C.1 — RISK MANAGEMENT ENGINE VERIFICATION TESTS")
    print("=" * 70)

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and engine
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("risk_analyst", "READ")

    engine = C1RiskManagementEngine(permission_gateway=perm_gateway, role="risk_analyst")
    assert engine.connect(), "Connection failed for C1RiskManagementEngine!"
    print(" -> SUCCESS: Risk engine established secure read-only session.")

    # 3. Test health and capabilities
    health = engine.health()
    assert health["status"] == "HEALTHY", "Health check failed!"
    caps = engine.capabilities()
    assert "calculate_position_sizing" in caps and "validate_risk_reward_ratio" in caps, "Capabilities mismatch!"
    print(f" -> SUCCESS: Health check passed. Capabilities declared: {len(caps)}")

    # 4. Test risk evaluation for compliant setup (R:R >= 1.5)
    valid_setup = {
        "symbol": "RELIANCE",
        "entry_price": 2500.0,
        "stop_loss": 2450.0,    # Risk = 50.0
        "target_price": 2600.0,  # Reward = 100.0 -> R:R = 2.0
        "account_capital": 500000.0,
        "risk_percentage": 1.0   # Max risk = 5000 -> Size = 100 shares
    }
    result = engine.evaluate_position_risk(valid_setup, min_rr_ratio=1.5)
    assert result.is_risk_compliant is True, "Valid setup failed risk compliance!"
    assert result.risk_reward_ratio == 2.0, "Risk-reward calculation mismatch!"
    assert result.position_size == 100, "Position sizing calculation mismatch!"
    assert result.has_execution_payload is False, "Execution safety invariant violated!"
    print(f" -> SUCCESS: Risk evaluation passed. R:R={result.risk_reward_ratio}, Position Size={result.position_size}")

    # 5. Test risk evaluation for non-compliant setup (R:R < 1.5)
    invalid_setup = {
        "symbol": "TCS",
        "entry_price": 3500.0,
        "stop_loss": 3450.0,    # Risk = 50.0
        "target_price": 3550.0,  # Reward = 50.0 -> R:R = 1.0 (Below 1.5)
        "account_capital": 500000.0,
        "risk_percentage": 1.0
    }
    fail_result = engine.evaluate_position_risk(invalid_setup, min_rr_ratio=1.5)
    assert fail_result.is_risk_compliant is False, "Non-compliant setup incorrectly marked valid!"
    print(f" -> SUCCESS: Non-compliant R:R correctly rejected: R:R={fail_result.risk_reward_ratio}")

    # 6. Test unauthorized access block
    unauth_gateway = PermissionGateway()
    unauth_engine = C1RiskManagementEngine(permission_gateway=unauth_gateway, role="unauthorized_role")
    try:
        unauth_engine.connect()
        raise AssertionError("SECURITY FAILURE: Unauthorized role bypassed permission check!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized risk connection successfully blocked: {e}")

    engine.disconnect()
    print("=" * 70)
    print("TRACK C.1 RISK MANAGEMENT ENGINE VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_c_1_tests()