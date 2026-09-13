import logging
from typing import Any, Dict, List, Optional
from registry.resolver import CapabilityResolver
from security.gateway import PermissionGateway
from contracts import (
    MarketQuote, 
    FundamentalMetric, 
    ScanResult, 
    TradingSignal, 
    EarningsEvent, 
    NewsItem, 
    MacroIndicator
)

logger = logging.getLogger("NormalizationPipeline")

class NormalizationPipeline:
    """
    Central pipeline that coordinates multi-adapter data retrieval, 
    permission verification, and canonical normalization.
    """

    def __init__(self, resolver: CapabilityResolver, gateway: PermissionGateway):
        self.resolver = resolver
        self.gateway = gateway

    def ingest_symbol_report(self, symbol: str) -> Dict[str, Any]:
        """
        Aggregates and normalizes multi-source data for a given symbol 
        across market quotes, fundamentals, technicals, and news.
        """
        logger.info(f"Running normalization pipeline for symbol: {symbol}")
        report: Dict[str, Any] = {"symbol": symbol.upper(), "data": {} }

        # 1. Market Quote (NSE)
        try:
            raw_quote = self.resolver.execute_via_capability(
                namespace="market.quotes",
                method_name="read",
                required_operation="READ",
                identifier=symbol
            )
            adapter = self.resolver.resolve_adapter("market.quotes")
            canonical_quote = adapter.normalize(raw_quote, MarketQuote)
            report["data"]["market_quote"] = canonical_quote.model_dump()
        except Exception as e:
            logger.error(f"Failed to ingest market quote for {symbol}: {e}")
            report["data"]["market_quote"] = None

        # 2. Fundamental Metrics (Screener)
        try:
            raw_fund = self.resolver.execute_via_capability(
                namespace="fundamental.metrics",
                method_name="read",
                required_operation="READ",
                identifier=symbol
            )
            adapter = self.resolver.resolve_adapter("fundamental.metrics")
            canonical_fund = adapter.normalize(raw_fund, FundamentalMetric)
            report["data"]["fundamentals"] = canonical_fund.model_dump()
        except Exception as e:
            logger.error(f"Failed to ingest fundamentals for {symbol}: {e}")
            report["data"]["fundamentals"] = None

        # 3. Technical Indicator / Signal (TradingView)
        try:
            raw_signal = self.resolver.execute_via_capability(
                namespace="technical.indicators",
                method_name="read",
                required_operation="READ",
                identifier=symbol
            )
            adapter = self.resolver.resolve_adapter("technical.indicators")
            canonical_signal = adapter.normalize(raw_signal, TradingSignal)
            report["data"]["technical_signal"] = canonical_signal.model_dump()
        except Exception as e:
            logger.error(f"Failed to ingest technical signal for {symbol}: {e}")
            report["data"]["technical_signal"] = None

        # 4. News Feed
        try:
            raw_news = self.resolver.execute_via_capability(
                namespace="news.feed",
                method_name="read",
                required_operation="READ",
                identifier=symbol
            )
            adapter = self.resolver.resolve_adapter("news.feed")
            canonical_news = adapter.normalize(raw_news, NewsItem)
            report["data"]["news"] = canonical_news.model_dump()
        except Exception as e:
            logger.error(f"Failed to ingest news for {symbol}: {e}")
            report["data"]["news"] = None

        return report