import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from integrations.chartink_adapter import ChartinkAdapter
from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from contracts import ScanResult

def run_chartink_tests():
    print("Initializing P2.4 - Chartink Adapter Integration Tests...")
    
    resolver = CapabilityResolver()
    adapter = ChartinkAdapter()
    assert adapter.connect() == True

    # Register under abstract capability namespace 'technical.scanner'
    resolver.register_provider(ProviderRegistration(
        provider_id="chartink_live",
        namespace="technical.scanner",
        adapter_instance=adapter,
        priority=10
    ))

    # Test dynamic execution of read operation via capability namespace
    raw_scan = resolver.execute_via_capability(
        namespace="technical.scanner",
        method_name="read",
        required_operation="READ",
        identifier="volume_breakout"
    )

    # Test normalization into canonical model using model_dump()
    canonical_scan = adapter.normalize(raw_scan, ScanResult)
    assert canonical_scan.scanner_name == "volume_breakout"
    assert "RELIANCE" in canonical_scan.matched_symbols
    print(f"Canonical Scan Result Normalized Successfully: {canonical_scan.model_dump()}")

    print("P2.4 Chartink Adapter Tests Passed Successfully!")

if __name__ == "__main__":
    run_chartink_tests()