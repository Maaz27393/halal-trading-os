import sys
import os

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from security.gateway import PermissionGateway
from registry.resolver import CapabilityResolver
from registry.models import ProviderRegistration
from integrations.nse_adapter import NSEAdapter
from integrations.screener_adapter import ScreenerAdapter
from integrations.tradingview_adapter import TradingViewAdapter
from integrations.news_adapter import NewsAdapter
from pipelines.normalization_pipeline import NormalizationPipeline

def run_orchestration_verification():
    print("=" * 60)
    print("MULTI-PROVIDER ORCHESTRATION VERIFICATION (Batch 3)")
    print("=" * 60)

    gateway = PermissionGateway()
    resolver = CapabilityResolver()

    # Register all primary adapters
    resolver.register_provider(ProviderRegistration("nse_live", "market.quotes", NSEAdapter(), 10))
    resolver.register_provider(ProviderRegistration("screener_live", "fundamental.metrics", ScreenerAdapter(), 10))
    resolver.register_provider(ProviderRegistration("tv_live", "technical.indicators", TradingViewAdapter(), 10))
    resolver.register_provider(ProviderRegistration("news_live", "news.feed", NewsAdapter(), 10))

    pipeline = NormalizationPipeline(resolver=resolver, gateway=gateway)

    symbol = "TCS"
    print(f"\nExecuting multi-source ingestion report for {symbol}...")
    try:
        report = pipeline.ingest_symbol_report(symbol)
        print("Multi-Provider Report Generated Successfully:")
        import json
        print(json.dumps(report, indent=2, default=str))
        print("\n[Success] Multi-Provider Orchestration Verification Passed!")
    except Exception as e:
        print(f"[Error] Orchestration verification failed: {e}")

if __name__ == "__main__":
    run_orchestration_verification()
