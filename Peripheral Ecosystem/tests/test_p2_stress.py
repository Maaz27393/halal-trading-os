import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from registry.resolver import CapabilityResolver
from registry.models import ProviderRegistration
from security.gateway import PermissionGateway
from integrations.fallback_adapters import FaultyNSEAdapter, BackupNSEAdapter
from contracts import MarketQuote

def run_stress_tests():
    print("Initializing P2.10 - Health & Fallback Stress Tests...")

    resolver = CapabilityResolver()

    # Register faulty primary adapter with high priority (1)
    resolver.register_provider(ProviderRegistration(
        provider_id="primary_faulty_nse",
        namespace="market.quotes",
        adapter_instance=FaultyNSEAdapter(),
        priority=1
    ))

    # Register backup adapter with lower priority (5)
    resolver.register_provider(ProviderRegistration(
        provider_id="secondary_backup_nse",
        namespace="market.quotes",
        adapter_instance=BackupNSEAdapter(),
        priority=5
    ))

    # Test automatic failover during execution
    print("Invoking read via namespace 'market.quotes' (Expecting primary failure & seamless fallback)...")
    raw_quote = resolver.execute_via_capability(
        namespace="market.quotes",
        method_name="read",
        required_operation="READ",
        identifier="RELIANCE"
    )

    # Resolve active adapter and normalize
    adapter = resolver.resolve_adapter("market.quotes")
    canonical_quote = adapter.normalize(raw_quote, MarketQuote)

    assert canonical_quote.source_provider == "backup_nse_provider"
    assert canonical_quote.last_price == 2852.0
    print(f"Fallback Successful! Normalized Quote: {canonical_quote.model_dump()}")

    print("P2.10 Health & Fallback Stress Tests Passed Successfully!")

if __name__ == "__main__":
    run_stress_tests()