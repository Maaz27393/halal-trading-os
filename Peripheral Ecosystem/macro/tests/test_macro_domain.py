import unittest
from macro.adapters.macro_adapter import DomainMacroAdapter
from macro.health.macro_health import MacroHealthChecker

class TestMacroDomain(unittest.TestCase):
    def test_macro_adapter_and_normalization(self):
        adapter = DomainMacroAdapter()
        health_checker = MacroHealthChecker(adapter)
        
        health = health_checker.check()
        self.assertEqual(health["status"], "healthy")
        self.assertTrue(health["read_only"])

        indicator = adapter.fetch_indicator("REPO_RATE")
        self.assertEqual(indicator.source_provider, "macro_provider")
        self.assertEqual(indicator.indicator_name, "REPO_RATE")
        self.assertEqual(indicator.value, 6.5)

if __name__ == "__main__":
    unittest.main()
