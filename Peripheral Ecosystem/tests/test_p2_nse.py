import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from integrations.nse_adapter import NSEAdapter
from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from contracts import MarketQuote

def run_nse_tests():
    print("Initializing P2.2 - NSE Adapter Integration Tests...")
    
    resolver = CapabilityResolver()
    adapter = NSEAdapter()
    assert adapter.connect() == True

    # Register under abstract capability namespace 'market.quotes'
    resolver.register_provider(ProviderRegistration(
        provider_id="nse_live",
        namespace="market.quotes",
        adapter_instance=adapter,
        priority=10
    ))

    # Test dynamic execution of read operation via capability namespace
    raw_quote = resolver.execute_via_capability(
        namespace="market.quotes",
        method_name="read",
        required_operation="READ",
        identifier="RELIANCE"
    )

    # Test normalization into canonical model
    canonical_quote = adapter.normalize(raw_quote, MarketQuote)
    assert canonical_quote.symbol == "RELIANCE"
    assert canonical_quote.last_price == 2850.50
    print(f"Canonical Market Quote Normalized Successfully: {canonical_quote.dict()}")

    print("P2.2 NSE Adapter Tests Passed Successfully!")

if __name__ == "__main__":
    run_nse_tests()