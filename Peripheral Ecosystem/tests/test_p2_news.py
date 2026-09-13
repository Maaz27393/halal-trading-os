import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from integrations.news_adapter import NewsAdapter
from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from contracts import NewsItem

def run_news_tests():
    print("Initializing P2.7 - News Adapter Integration Tests...")
    
    resolver = CapabilityResolver()
    adapter = NewsAdapter()
    assert adapter.connect() == True

    # Register under abstract capability namespace 'news.feed'
    resolver.register_provider(ProviderRegistration(
        provider_id="news_feed_live",
        namespace="news.feed",
        adapter_instance=adapter,
        priority=10
    ))

    # Test dynamic execution of read operation via capability namespace
    raw_news = resolver.execute_via_capability(
        namespace="news.feed",
        method_name="read",
        required_operation="READ",
        identifier="nifty"
    )

    # Test normalization into canonical model using model_dump()
    canonical_news = adapter.normalize(raw_news, NewsItem)
    assert "Nifty" in canonical_news.title or "nifty" in canonical_news.title.lower()
    print(f"Canonical News Item Normalized Successfully: {canonical_news.model_dump()}")

    print("P2.7 News Adapter Tests Passed Successfully!")

if __name__ == "__main__":
    run_news_tests()