import sys
import os

# Point Python path to Peripheral Ecosystem root
PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from track_b_workspace.analytics_engine.screener_adapter import B1ScreenerAnalyticsEngine

def run_b_1_tests():
    print("=" * 70)
    print("STARTING TRACK B.1 — ADVANCED ANALYTICS & SCREENER VERIFICATION TESTS")
    print("=" * 70)

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and engine
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")

    engine = B1ScreenerAnalyticsEngine(permission_gateway=perm_gateway, role="analyst_agent")
    assert engine.connect(), "Connection failed for B1ScreenerAnalyticsEngine!"
    print(" -> SUCCESS: Analytics engine established secure read-only session.")

    # 3. Test health and capabilities
    health = engine.health()
    assert health["status"] == "HEALTHY", "Health check failed!"
    caps = engine.capabilities()
    assert "filter_screener_universe" in caps, "Capabilities mismatch!"
    print(f" -> SUCCESS: Health check passed. Capabilities declared: {len(caps)}")

    # 4. Test screening universe filtering
    raw_universe = [
        {"symbol": "RELIANCE", "sector": "Energy", "roe": 15.5, "rsi": 58.4, "volume_spike_ratio": 1.4, "is_compliant": True},
        {"symbol": "TCS", "sector": "IT", "roe": 28.1, "rsi": 74.2, "volume_spike_ratio": 1.8, "is_compliant": True}, # RSI too high (>70)
        {"symbol": "INFY", "sector": "IT", "roe": 10.2, "rsi": 52.0, "volume_spike_ratio": 1.1, "is_compliant": True}, # ROE & Vol too low
        {"symbol": "HDFC", "sector": "Banking", "roe": 16.8, "rsi": 49.5, "volume_spike_ratio": 1.6, "is_compliant": True}
    ]

    criteria = {"min_roe": 12.0, "max_rsi": 70.0, "min_volume_spike": 1.2}
    filtered_results = engine.process_universe(raw_universe, criteria)

    assert len(filtered_results) == 2, f"Expected exactly 2 compliant stocks, got {len(filtered_results)}!"
    symbols = [item.symbol for item in filtered_results]
    assert "RELIANCE" in symbols and "HDFC" in symbols, "Filtered symbol mismatch!"
    print(f" -> SUCCESS: Screener universe successfully filtered. Retained stocks: {symbols}")

    # 5. Test unauthorized access block
    unauth_gateway = PermissionGateway()
    unauth_engine = B1ScreenerAnalyticsEngine(permission_gateway=unauth_gateway, role="unauthorized_role")
    try:
        unauth_engine.connect()
        raise AssertionError("SECURITY FAILURE: Unauthorized role bypassed permission check!")
    except PermissionError as e:
        print(f" -> SUCCESS: Unauthorized analytics connection successfully blocked: {e}")

    engine.disconnect()
    print("=" * 70)
    print("TRACK B.1 ANALYTICS ENGINE VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_b_1_tests()