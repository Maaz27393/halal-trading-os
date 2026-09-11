import json
import unittest
from retrieval_adapter import query_retrieval_api, get_qwen_tool_definition


class TestRetrievalAdapterContract(unittest.TestCase):

    def setUp(self):
        self.test_query = "Who has authority to approve a change to the Trading OS?"
        self.payload = query_retrieval_api(self.test_query)

    def test_json_serializability(self):
        """Verify payload safely serializes to standard JSON format without circular refs or non-serializable objects."""
        try:
            dumped = json.dumps(self.payload)
            self.assertIsInstance(dumped, str)
        except (TypeError, OverflowError) as e:
            self.fail(f"Payload failed JSON serialization: {e}")

    def test_top_level_schema(self):
        """Validate top-level keys and data types."""
        required_keys = {
            "api_version": str,
            "retrieval_version": str,
            "query": str,
            "intent": str,
            "confidence": (float, int),
            "match_quality": str,
            "structured_evidence": dict,
            "results": list,
            "vault_status": dict,
        }

        for key, expected_type in required_keys.items():
            self.assertIn(key, self.payload, f"Missing top-level key: '{key}'")
            self.assertIsInstance(
                self.payload[key],
                expected_type,
                f"Key '{key}' expected type {expected_type}, got {type(self.payload[key])}",
            )

        self.assertEqual(self.payload["api_version"], "1.0")
        self.assertEqual(self.payload["retrieval_version"], "3.6")

    def test_vault_status_structure(self):
        """Validate vault_status metadata sub-schema."""
        status = self.payload.get("vault_status", {})
        for key in ["files_seen", "files_loaded", "files_skipped"]:
            self.assertIn(key, status, f"Missing '{key}' in vault_status")
            self.assertIsInstance(status[key], int)

    def test_results_item_schema(self):
        """Validate public result item field presence and types."""
        results = self.payload.get("results", [])
        self.assertGreater(len(results), 0, "Results list should not be empty for a standard query")

        expected_fields = {
            "title": str,
            "path": str,
            "type": str,
            "status": str,
            "evidence": str,
            "score": (int, float),
            "snippet": str,
        }

        for idx, item in enumerate(results):
            for field, expected_type in expected_fields.items():
                self.assertIn(field, item, f"Result index {idx} missing field: '{field}'")
                self.assertIsInstance(
                    item[field],
                    expected_type,
                    f"Result index {idx} field '{field}' expected {expected_type}, got {type(item[field])}",
                )

    def test_qwen_tool_definition(self):
        """Validate Qwen/OpenAI tool schema format."""
        tool_def = get_qwen_tool_definition()
        self.assertEqual(tool_def.get("type"), "function")
        self.assertIn("function", tool_def)
        self.assertEqual(tool_def["function"]["name"], "vault_search")
        self.assertIn("parameters", tool_def["function"])
        self.assertIn("query", tool_def["function"]["parameters"]["properties"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
