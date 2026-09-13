import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from integrations.macro_adapter import MacroAdapter
from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from contracts import MacroIndicator

def run_macro_tests():
    print("Initializing P2.8 - Macro Adapter Integration Tests...")
    
    resolver = CapabilityResolver()
    adapter = MacroAdapter()
    assert adapter.connect() == True

    # Register under abstract capability namespace 'macro.indicators'
    resolver.register_provider(ProviderRegistration(
        provider_id="macro_data_live",
        namespace="macro.indicators",
        adapter_instance=adapter,
        priority=10
    ))

    # Test dynamic execution of read operation via capability namespace
    raw_macro = resolver.execute_via_capability(
        namespace="macro.indicators",
        method_name="read",
        required_operation="READ",
        identifier="repo_rate"
    )

    # Test normalization into canonical model using model_dump()
    canonical_macro = adapter.normalize(raw_macro, MacroIndicator)
    assert canonical_macro.indicator_name == "REPO_RATE"
    assert canonical_macro.value == 6.5
    print(f"Canonical Macro Indicator Normalized Successfully: {canonical_macro.model_dump()}")

    print("P2.8 Macro Adapter Tests Passed Successfully!")

if __name__ == "__main__":
    run_macro_tests()