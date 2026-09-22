import unittest
import os
from power_bi_integration.exporters.model_exporter import PowerBIModelExporter

class TestPowerBIModelExporter(unittest.TestCase):
    def test_export_pipeline(self):
        exporter = PowerBIModelExporter()
        files = exporter.export_models()

        self.assertIn("dim_providers", files)
        self.assertIn("fact_system_health", files)
        self.assertIn("dim_governance", files)

        for key, path in files.items():
            self.assertTrue(os.path.exists(path), f"Export file missing for {key}: {path}")
            print(f"[Verified] Exported Power BI Table [{key}] -> {path}")

if __name__ == "__main__":
    unittest.main()
