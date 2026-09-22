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

def run_snapshot_verification():
    print("=" * 60)
    print("NSE SNAPSHOT & NORMALIZATION VERIFICATION (Batch 3)")
    print("=" * 60)

    gateway = PermissionGateway()
    resolver = CapabilityResolver()
    nse_adapter = NSEAdapter(config={"gateway": gateway})

    resolver.register_provider(ProviderRegistration(
        provider_id="nse_live",
        namespace="market.quotes",
        adapter_instance=nse_adapter,
        priority=10
    ))

    symbol = "INFY"
    print(f"\nFetching snapshot for {symbol} via P2 CapabilityResolver...")
    try:
        raw_data = resolver.execute_via_capability(
            namespace="market.quotes",
            method_name="read",
            required_operation="READ",
            identifier=symbol
        )
        canonical_quote = nse_adapter.normalize(raw_data, MarketQuote)
        print("Snapshot Normalized Successfully:")
        print(canonical_quote.model_dump_json(indent=2))
        print("\n[Success] verify_nse_snapshot.py passed!")
    except Exception as e:
        print(f"[Error] Snapshot verification failed: {e}")

if __name__ == "__main__":
    run_snapshot_verification()
