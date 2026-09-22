import unittest
from datetime import datetime, timezone, timedelta
from data_quality.contracts.quality_contract import QualityState
from data_quality.gates.quality_gate import DataQualityGate

class TestPhase19DataQualityGate(unittest.TestCase):
    def setUp(self):
        self.gate = DataQualityGate(required_fields=["symbol", "price", "timestamp"], max_age_seconds=60)

    def test_gate_pass_valid_fresh_payload(self):
        now = datetime.now(timezone.utc)
        payload = {"symbol": "RELIANCE", "price": 2500.0, "timestamp": now.isoformat()}
        provenance = {"source": "NSE_API", "connector_version": "1.2.0"}

        metadata = self.gate.evaluate("NSE", payload, now, provenance)

        self.assertEqual(metadata.validation_status, QualityState.VALID)
        self.assertEqual(metadata.freshness_status, QualityState.FRESH)
        self.assertEqual(len(metadata.missing_fields), 0)
        self.assertEqual(len(metadata.validation_errors), 0)
        self.assertFalse(metadata.governance_flag)

    def test_gate_reject_missing_fields(self):
        now = datetime.now(timezone.utc)
        payload = {"symbol": "TCS"} # Missing price and timestamp fields
        provenance = {"source": "SCREENER"}

        metadata = self.gate.evaluate("SCREENER", payload, now, provenance)

        self.assertEqual(metadata.validation_status, QualityState.INCOMPLETE)
        self.assertIn("price", metadata.missing_fields)
        self.assertIn("timestamp", metadata.missing_fields)
        self.assertTrue(len(metadata.validation_errors) > 0)

    def test_gate_reject_stale_payload(self):
        old_time = datetime.now(timezone.utc) - timedelta(minutes=10) # Older than max_age_seconds (60s)
        payload = {"symbol": "INFY", "price": 1500.0, "timestamp": old_time.isoformat()}
        provenance = {"source": "CHARTINK"}

        metadata = self.gate.evaluate("CHARTINK", payload, old_time, provenance)

        self.assertEqual(metadata.freshness_status, QualityState.EXPIRED)
        self.assertNotEqual(metadata.validation_status, QualityState.VALID)

if __name__ == "__main__":
    unittest.main()
