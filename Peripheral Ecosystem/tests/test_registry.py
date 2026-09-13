import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver, CapabilityResolutionError
from connectors.base import BaseConnector
from contracts import FundamentalData

# Mock Adapter 1 (e.g., Screener v1)
class MockScreenerAdapter(BaseConnector):
    def connect(self) -> bool: return True
    def health(self) -> dict: return {"status": "healthy"}
    def capabilities(self) -> list: return ["READ", "SEARCH"]
    def read(self, identifier: str, **kwargs) -> str: return f"Data from Screener for {identifier}"
    def search(self, query: str, **kwargs) -> list: return [query]
    def normalize(self, raw_data, target_model): return target_model(source_provider="screener", symbol="TEST")
    def disconnect(self) -> bool: return True

# Mock Adapter 2 (e.g., Future Provider replacement)
class MockNewFundamentalAdapter(BaseConnector):
    def connect(self) -> bool: return True
    def health(self) -> dict: return {"status": "healthy"}
    def capabilities(self) -> list: return ["READ"]
    def read(self, identifier: str, **kwargs) -> str: return f"Data from NEW provider for {identifier}"
    def search(self, query: str, **kwargs) -> list: return []
    def normalize(self, raw_data, target_model): return target_model(source_provider="new_provider", symbol="TEST")
    def disconnect(self) -> bool: return True

def run_registry_tests():
    resolver = CapabilityResolver()

    adapter_old = MockScreenerAdapter("screener")
    adapter_new = MockNewFundamentalAdapter("new_provider")

    # Register old provider with higher priority (lower number)
    resolver.register_provider(ProviderRegistration(
        provider_id="screener_v1",
        namespace="fundamental.metrics",
        adapter_instance=adapter_old,
        priority=10
    ))

    # Register new provider with lower priority (fallback)
    resolver.register_provider(ProviderRegistration(
        provider_id="provider_v2",
        namespace="fundamental.metrics",
        adapter_instance=adapter_new,
        priority=20
    ))

    # 1. Test standard resolution (should pick screener_v1 due to priority 10)
    resolved = resolver.resolve("fundamental.metrics")
    assert resolved.provider_id == "screener_v1"
    print(f"Primary Resolution Passed: {resolved.provider_id}")

    # 2. Test workflow execution without hard-coding provider names
    result = resolver.execute_via_capability("fundamental.metrics", "read", "READ", identifier="RELIANCE")
    assert "Screener" in result
    print(f"Capability Execution Result: {result}")

    # 3. Test seamless swappability / fallback (simulate screener failure by marking unhealthy)
    resolver._registry["fundamental.metrics"][0].health_status = "unhealthy"
    
    fallback_resolved = resolver.resolve("fundamental.metrics")
    assert fallback_resolved.provider_id == "provider_v2"
    print(f"Automated Fallback Resolution Passed: {fallback_resolved.provider_id}")

    fallback_result = resolver.execute_via_capability("fundamental.metrics", "read", "READ", identifier="TCS")
    assert "NEW provider" in fallback_result
    print(f"Fallback Execution Result: {fallback_result}")

if __name__ == "__main__":
    run_registry_tests()