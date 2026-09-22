import unittest
from interactive_dashboard.frontend.dashboard_renderer import InteractiveOperationsDashboard

class TestInteractiveDashboard(unittest.TestCase):
    def test_dashboard_rendering(self):
        dashboard = InteractiveOperationsDashboard()
        view = dashboard.render_control_room()

        self.assertIn("HALAL TRADING OS — INTERACTIVE OPERATIONS CONTROL ROOM", view)
        self.assertIn("SYSTEM OVERVIEW", view)
        self.assertIn("PROVIDER HEALTH", view)
        self.assertIn("GOVERNANCE SAFEGUARDS", view)
        self.assertIn("STRICTLY_READ_ONLY", view)

        print(view)

if __name__ == "__main__":
    unittest.main()
