import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from integrations.earnings_adapter import EarningsAdapter
from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from contracts import EarningsEvent

def run_earnings_tests():
    print("Initializing P2.6 - Earnings Adapter Integration Tests...")
    
    resolver = CapabilityResolver()
    adapter = EarningsAdapter()
    assert adapter.connect() == True

    # Register under abstract capability namespace 'macro.events'
    resolver.register_provider(ProviderRegistration(
        provider_id="earnings_calendar_live",
        namespace="macro.events",
        adapter_instance=adapter,
        priority=10
    ))

    # Test dynamic execution of read operation via capability namespace
    raw_event = resolver.execute_via_capability(
        namespace="macro.events",
        method_name="read",
        required_operation="READ",
        identifier="INFY"
    )

    # Test normalization into canonical model using model_dump()
    canonical_event = adapter.normalize(raw_event, EarningsEvent)
    assert canonical_event.symbol == "INFY"
    assert canonical_event.date == "2026-10-15"
    print(f"Canonical Earnings Event Normalized Successfully: {canonical_event.model_dump()}")

    print("P2.6 Earnings Adapter Tests Passed Successfully!")

if __name__ == "__main__":
    run_earnings_tests()