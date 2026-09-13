import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from integrations.tradingview_adapter import TradingViewAdapter
from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from contracts import TradingSignal

def run_tradingview_tests():
    print("Initializing P2.5 - TradingView Adapter Integration Tests...")
    
    resolver = CapabilityResolver()
    adapter = TradingViewAdapter()
    assert adapter.connect() == True

    # Register under abstract capability namespace 'technical.indicators'
    resolver.register_provider(ProviderRegistration(
        provider_id="tradingview_webhook",
        namespace="technical.indicators",
        adapter_instance=adapter,
        priority=10
    ))

    # Test dynamic execution of read operation via capability namespace
    raw_signal = resolver.execute_via_capability(
        namespace="technical.indicators",
        method_name="read",
        required_operation="READ",
        identifier="RELIANCE"
    )

    # Test normalization into canonical model using model_dump()
    canonical_signal = adapter.normalize(raw_signal, TradingSignal)
    assert canonical_signal.symbol == "RELIANCE"
    assert canonical_signal.signal_type == "EMA_CROSSOVER_BULLISH"
    print(f"Canonical Trading Signal Normalized Successfully: {canonical_signal.model_dump()}")

    print("P2.5 TradingView Adapter Tests Passed Successfully!")

if __name__ == "__main__":
    run_tradingview_tests()