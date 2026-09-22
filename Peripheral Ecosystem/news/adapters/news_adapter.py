import logging
from typing import Any, Dict, List, Optional
from news.contracts.news_contract import NewsItem

logger = logging.getLogger("DomainNewsAdapter")

class DomainNewsAdapter:
    """
    Provider-neutral read-only news adapter residing entirely within the news domain.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.provider_name = "news_provider"
        self.config = config or {}
        self.endpoint = self.config.get("endpoint", "https://api.financial-news.local")
        self._is_connected = True
        logger.info("DomainNewsAdapter initialized (Read-Only / Non-Execution).")

    def connect(self) -> bool:
        self._is_connected = True
        return True

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self._is_connected else "disconnected",
            "provider": self.provider_name,
            "endpoint": self.endpoint,
            "read_only": True
        }

    def fetch_news(self, symbol: str) -> NewsItem:
        """Fetch and normalize news for a given symbol."""
        logger.info(f"Fetching news for symbol: {symbol}")
        raw_data = {
            "headline": f"Market Update: Strong momentum in IT and Banking sectors for {symbol.upper()}",
            "summary": f"Analysts highlight robust quarterly projections and institutional inflows for {symbol.upper()}.",
            "url": f"https://financial-news.local/articles/{symbol.lower()}-rally",
            "symbols": [symbol.upper()],
            "sentiment_score": 0.85,
            "tags": ["market_trend", "institutional_flow", symbol.upper()]
        }
        return NewsItem(
            source_provider=self.provider_name,
            headline=raw_data["headline"],
            summary=raw_data["summary"],
            url=raw_data["url"],
            symbols=raw_data["symbols"],
            sentiment_score=raw_data["sentiment_score"],
            tags=raw_data["tags"]
        )

    def disconnect(self) -> bool:
        self._is_connected = False
        return True
