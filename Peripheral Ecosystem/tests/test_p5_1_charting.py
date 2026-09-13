import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p5_expansion.charting_exporter import AdvancedChartingExporter
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_p5_1_test():
    print("Initializing P5.1 - Advanced Charting & Pattern Exporter Verification...")

    # 1. Verify frozen core invariant
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Setup permissions and vault target
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "READ")
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    exporter = AdvancedChartingExporter(permission_gateway=perm_gateway, vault_base_path=vault_base)

    # 3. Execute chart export workflow
    test_symbols = ["RELIANCE", "TCS"]
    exported_path = exporter.generate_and_export_charts(test_symbols, caller_role="analyst_agent")

    print(f"Exported Chart Artifact Path: {exported_path}")
    assert os.path.exists(exported_path), "Export Error: Advanced charting markdown file was not created!"

    with open(exported_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Bullish EMA 20/50 Pullback" in content

    print("P5.1 Advanced Charting & Pattern Exporter Verified Successfully!")

if __name__ == "__main__":
    run_p5_1_test()