import sys
import os

# Add root 'Peripheral Ecosystem' directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from registry.resolver import CapabilityResolver
from registry.models import ProviderRegistration
from security.gateway import PermissionGateway
from pipelines.normalization_pipeline import NormalizationPipeline

# Import adapters
from integrations.nse_adapter import NSEAdapter
from integrations.screener_adapter import ScreenerAdapter
from integrations.tradingview_adapter import TradingViewAdapter
from integrations.news_adapter import NewsAdapter

def run_pipeline_tests():
    print("Initializing P2.9 - Normalization Pipeline Integration Tests...")

    resolver = CapabilityResolver()
    gateway = PermissionGateway()

    # Register all key research adapters
    resolver.register_provider(ProviderRegistration("nse_live", "market.quotes", NSEAdapter(), 10))
    resolver.register_provider(ProviderRegistration("screener_live", "fundamental.metrics", ScreenerAdapter(), 10))
    resolver.register_provider(ProviderRegistration("tv_live", "technical.indicators", TradingViewAdapter(), 10))
    resolver.register_provider(ProviderRegistration("news_live", "news.feed", NewsAdapter(), 10))

    pipeline = NormalizationPipeline(resolver=resolver, gateway=gateway)

    # Execute consolidated multi-source ingestion report for Reliance
    report = pipeline.ingest_symbol_report("RELIANCE")

    assert report["symbol"] == "RELIANCE"
    assert report["data"]["market_quote"]["symbol"] == "RELIANCE"
    assert report["data"]["fundamentals"]["symbol"] == "RELIANCE"
    assert report["data"]["technical_signal"]["symbol"] == "RELIANCE"
    
    print("Consolidated Multi-Source Report Generated Successfully:")
    import json
    print(json.dumps(report, indent=2, default=str))

    print("P2.9 Normalization Pipeline Tests Passed Successfully!")

if __name__ == "__main__":
    run_pipeline_tests()