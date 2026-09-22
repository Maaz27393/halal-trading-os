import sys
import os

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from security.gateway import PermissionGateway
from registry.resolver import CapabilityResolver
from registry.models import ProviderRegistration
from integrations.screener_adapter import ScreenerAdapter
from contracts import FundamentalMetric

def run_screener_tests():
    print("=" * 60)
    print("SCREENER ADAPTER & CAPABILITY RESOLVER VERIFICATION (Batch 3)")
    print("=" * 60)

    # 1. Initialize Gateway & Resolver
    print("\n[1] Initializing Security Gateway & Capability Resolver...")
    gateway = PermissionGateway()
    resolver = CapabilityResolver()

    # Register Screener Adapter under 'fundamental.metrics'
    screener_adapter = ScreenerAdapter(config={"gateway": gateway})
    resolver.register_provider(ProviderRegistration(
        provider_id="screener_live",
        namespace="fundamental.metrics",
        adapter_instance=screener_adapter,
        priority=10
    ))
    print("Capability Resolver & Screener Adapter: OK")

    # 2. Test Health & Capabilities
    print("\n[2] Verifying Adapter Health and Read-Only Governance...")
    health = screener_adapter.health()
    print(f"Health Status: {health}")
    print(f"Supported Capabilities: {screener_adapter.capabilities()}")

    # 3. Test Read & Normalization via Resolver
    symbol = "TCS"
    print(f"\n[3] Testing Fundamental Data Read & Canonical Normalization for '{symbol}'...")
    try:
        raw_fundamentals = resolver.execute_via_capability(
            namespace="fundamental.metrics",
            method_name="read",
            required_operation="READ",
            identifier=symbol
        )
        canonical_metrics = screener_adapter.normalize(raw_fundamentals, FundamentalMetric)
        print("Canonical FundamentalMetric Generated Successfully:")
        print(canonical_metrics.model_dump_json(indent=2))
        print("\n[Success] Screener Operational Migration Verification Passed!")
    except Exception as e:
        print(f"\n[Error during Screener verification]: {e}")

if __name__ == "__main__":
    run_screener_tests()
