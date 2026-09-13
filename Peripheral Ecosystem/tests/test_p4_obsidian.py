import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.gateway import PermissionGateway
from p4_agents.obsidian_exporter import ObsidianVaultExporter
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_obsidian_exporter_test():
    print("Initializing P4.6 - Research-to-Obsidian Markdown Vault Exporter Verification...")

    # 1. Verify frozen core governance guardrail
    assert LIVE_AUTO_EXECUTION is False, "Governance Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Initialize security and vault bindings
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("analyst_agent", "WRITE")

    vault_base = "D:\\OBSIDIAN VAULT\\halal-trading-os"
    exporter = ObsidianVaultExporter(permission_gateway=perm_gateway, vault_base_path=vault_base)

    # 3. Test markdown export
    sample_markdown = """---
date: 2026-09-13
type: pre-market-briefing
bias: Moderately Bullish
guardrail: LIVE_AUTO_EXECUTION=FALSE
---

# Pre-Market Briefing - 2026-09-13

## Market Regime
- **Nifty Trend**: Bullish Pullback
- **India VIX**: 13.5
- **Market Bias**: Moderately Bullish

## Research Watchlist
- **RELIANCE**: Volume spike near daily support.
"""

    filename = "PreMarket_2026-09-13.md"
    exported_path = exporter.export_artifact("premarket", filename, sample_markdown, caller_role="analyst_agent")

    print(f"Exported File Path: {exported_path}")
    assert os.path.exists(exported_path), "Export Error: Markdown file was not created in the vault!"
    
    print("P4.6 Research-to-Obsidian Markdown Vault Exporter Verified Successfully!")

if __name__ == "__main__":
    run_obsidian_exporter_test()