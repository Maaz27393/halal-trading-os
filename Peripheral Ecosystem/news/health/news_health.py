from typing import Dict, Any
from news.adapters.news_adapter import DomainNewsAdapter

class NewsHealthChecker:
    def __init__(self, adapter: DomainNewsAdapter):
        self.adapter = adapter

    def check(self) -> Dict[str, Any]:
        return self.adapter.health()
