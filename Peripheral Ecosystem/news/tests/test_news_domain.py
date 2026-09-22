import unittest
from news.adapters.news_adapter import DomainNewsAdapter
from news.health.news_health import NewsHealthChecker

class TestNewsDomain(unittest.TestCase):
    def test_news_adapter_and_normalization(self):
        adapter = DomainNewsAdapter()
        health_checker = NewsHealthChecker(adapter)
        
        health = health_checker.check()
        self.assertEqual(health["status"], "healthy")
        self.assertTrue(health["read_only"])

        news_item = adapter.fetch_news("RELIANCE")
        self.assertEqual(news_item.source_provider, "news_provider")
        self.assertIn("RELIANCE", news_item.symbols)
        self.assertEqual(news_item.sentiment_score, 0.85)

if __name__ == "__main__":
    unittest.main()
