import unittest
from data_quality.contracts.quality_contract import DataQualityMetadata, QualityState

class TestDataQualityBaseline(unittest.TestCase):
    def test_quality_metadata_initialization(self):
        metadata = DataQualityMetadata(
            provider="NSE_FEED",
            validation_status=QualityState.VALID,
            freshness_status=QualityState.FRESH
        )
        self.assertEqual(metadata.provider, "NSE_FEED")
        self.assertEqual(metadata.validation_status, QualityState.VALID)
        self.assertFalse(metadata.governance_flag)

if __name__ == "__main__":
    unittest.main()
