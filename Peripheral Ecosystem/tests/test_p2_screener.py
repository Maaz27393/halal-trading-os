import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from integrations.screener_adapter import ScreenerAdapter
from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from contracts import FundamentalMetric

def run_screener_tests():
    print("Initializing P2.3 - Screener Adapter Integration Tests...")
    
    resolver = CapabilityResolver()
    adapter = ScreenerAdapter()
    assert adapter.connect() == True

    # Register under abstract capability namespace 'fundamental.metrics'
    resolver.register_provider(ProviderRegistration(
        provider_id="screener_live",
        namespace="fundamental.metrics",
        adapter_instance=adapter,
        priority=10
    ))

    # Test dynamic execution of read operation via capability namespace
    raw_fundamentals = resolver.execute_via_capability(
        namespace="fundamental.metrics",
        method_name="read",
        required_operation="READ",
        identifier="TCS"
    )

    # Test normalization into canonical model using model_dump()
    canonical_metric = adapter.normalize(raw_fundamentals, FundamentalMetric)
    assert canonical_metric.symbol == "TCS"
    assert canonical_metric.pe_ratio == 28.4
    print(f"Canonical Fundamental Metric Normalized Successfully: {canonical_metric.model_dump()}")

    print("P2.3 Screener Adapter Tests Passed Successfully!")

if __name__ == "__main__":
    run_screener_tests()