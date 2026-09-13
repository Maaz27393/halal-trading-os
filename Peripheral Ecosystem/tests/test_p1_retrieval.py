import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from integrations.retrieval_adapter import RetrievalV36Adapter
from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver, CapabilityResolutionError
from permissions.gateway import PermissionGateway, PermissionViolationError

def run_p1_tests():
    print("Initializing P1.1 - P1.6 Knowledge Integration Tests...")
    
    gateway = PermissionGateway(strict_mode=True)
    resolver = CapabilityResolver(permission_gateway=gateway)

    # 1. Instantiate adapter
    adapter = RetrievalV36Adapter()
    assert adapter.connect() == True

    # 2. Register under the abstract 'knowledge.search' capability namespace
    resolver.register_provider(ProviderRegistration(
        provider_id="retrieval_v36_primary",
        namespace="knowledge.search",
        adapter_instance=adapter,
        priority=10
    ))

    # 3. Test dynamic resolution and execution via capability namespace
    results = resolver.execute_via_capability(
        namespace="knowledge.search",
        method_name="search",
        required_operation="READ",
        query="intraday trading strategy"
    )
    
    assert len(results) > 0
    print(f"Knowledge Search Capability Result: {results}")

    # 4. Verify Read-Only Firewall Protection (Ensure no WRITE/EXECUTE can pass on this adapter)
    try:
        resolver.execute_via_capability(
            namespace="knowledge.search",
            method_name="read",
            required_operation="EXECUTE", # Should trigger firewall block / resolution failure
            identifier="test_id"
        )
        raise AssertionError("Firewall failed to block EXECUTE on read-only knowledge adapter!")
    except (PermissionViolationError, CapabilityResolutionError) as e:
        print(f"Gateway Successfully Blocked Unauthorized Operation: {e}")

    print("P1 Knowledge Integration Tests Passed Successfully!")

if __name__ == "__main__":
    run_p1_tests()