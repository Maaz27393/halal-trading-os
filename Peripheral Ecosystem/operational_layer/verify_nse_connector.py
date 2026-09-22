import sys
import os

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from security.gateway import PermissionGateway
from registry.resolver import CapabilityResolver
from registry.models import ProviderRegistration
from integrations.nse_adapter import NSEAdapter
from contracts import MarketQuote

def run_verification():
    print("=" * 60)
    print("NSE ADAPTER & CAPABILITY RESOLVER VERIFICATION (Batch 3)")
    print("=" * 60)

    # 1. Initialize Permission Gateway & Resolver
    print("\n[1] Initializing Security Gateway & Capability Resolver...")
    gateway = PermissionGateway()
    resolver = CapabilityResolver()

    # Register NSE Adapter under 'market.quotes'
    nse_adapter = NSEAdapter(config={"gateway": gateway})
    resolver.register_provider(ProviderRegistration(
        provider_id="nse_live",
        namespace="market.quotes",
        adapter_instance=nse_adapter,
        priority=10
    ))
    print("Capability Resolver & NSE Adapter: OK")

    # 2. Test Health & Capabilities
    print("\n[2] Verifying Adapter Health and Read-Only Governance...")
    health = nse_adapter.health()
    print(f"Health Status: {health}")
    print(f"Supported Capabilities: {nse_adapter.capabilities()}")

    # 3. Test Read & Normalization via Resolver
    print("\n[3] Testing Live Data Read & Canonical Normalization for 'RELIANCE'...")
    try:
        raw_quote = resolver.execute_via_capability(
            namespace="market.quotes",
            method_name="read",
            required_operation="READ",
            identifier="RELIANCE"
        )
        canonical_quote = nse_adapter.normalize(raw_quote, MarketQuote)
        print("Canonical MarketQuote Generated Successfully:")
        print(canonical_quote.model_dump_json(indent=2))
        print("\n[Success] NSE Operational Migration Verification Passed!")
    except Exception as e:
        print(f"\n[Error during NSE verification]: {e}")

if __name__ == "__main__":
    run_verification()
