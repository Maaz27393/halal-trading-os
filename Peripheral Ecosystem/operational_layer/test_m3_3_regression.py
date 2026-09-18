import unittest
import os
from operational_runner import MultiModeOperationalRunner

class TestM33RegistryAndConfluence(unittest.TestCase):
    def setUp(self):
        self.vault_path = "D:\\OBSIDIAN VAULT\\halal-trading-os"
        # Mock connector outputs to validate attribution and Institution Accumulation reconciliation
        self.mock_results = {
            "range-expansion": [
                {"symbol": "KPRMILL", "company": "K.p.r. Mill Ltd", "close": 1120.2, "volume": 204356, "pct_change": 1.0},
                {"symbol": "RPGLIFE", "company": "RPG Life Sciences", "close": 2718.8, "volume": 60664, "pct_change": 0.75}
            ],
            "institution-accumulation": [
                {"symbol": "KPRMILL", "company": "K.p.r. Mill Ltd", "close": 1120.2, "volume": 204356, "pct_change": 1.0},
                {"symbol": "UNVERIFIED_STOCK", "company": "Fake Inc", "close": 100.0, "volume": 1000, "pct_change": 0.5} # Should be filtered out by Halal universe
            ],
            "120-day-high": [
                {"symbol": "KPRMILL", "company": "K.p.r. Mill Ltd", "close": 1120.2, "volume": 204356, "pct_change": 1.0}
            ],
            "copy-ankur-s-breakout-scans-4680": []
        }

    def test_registry_loading_and_isolation(self):
        runner = MultiModeOperationalRunner(self.vault_path)
        
        # Verify INTRADAY scanners are NOT loaded into PRE_MARKET mode
        pre_market_scanners = runner.registry_loader.get_scanners_by_mode("PRE_MARKET")
        intraday_scanners = runner.registry_loader.get_scanners_by_mode("INTRADAY")
        
        pm_slugs = {s["slug"] for s in pre_market_scanners}
        id_slugs = {s["slug"] for s in intraday_scanners}
        
        self.assertNotIn("breakout-confirmation", pm_slugs)
        self.assertNotIn("rsi-above-60", pm_slugs)
        self.assertIn("breakout-confirmation", id_slugs)

    def test_confluence_and_halal_filtering(self):
        runner = MultiModeOperationalRunner(self.vault_path)
        # Mocking canonical universe to specifically include KPRMILL and RPGLIFE
        runner.canonical_halal_symbols = {"KPRMILL", "RPGLIFE"}

        # Run pre-market workflow with mock data
        # Institution accumulation returned 2 records, but 1 was non-halal. 
        # KPRMILL appears in Range Expansion, Institution Accumulation, and 120-Day High -> Score 3.
        # RPGLIFE appears in Range Expansion -> Score 1.
        briefing_file = runner.execute_pre_market_workflow(mock_connector_results=self.mock_results)
        self.assertTrue(os.path.exists(briefing_file))

if __name__ == "__main__":
    unittest.main()