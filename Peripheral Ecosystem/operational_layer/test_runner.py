import sys
import os

PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from operational_layer.daily_runner import OperationalDailyRunner

def test_operational_runner():
    print("=" * 70)
    print("RUNNING OPERATIONAL LAYER v1: DAILY RUNNER & BRIEFING TEST")
    print("=" * 70)

    runner = OperationalDailyRunner()
    result = runner.run_morning_pipeline()

    assert result["status"] == "SUCCESS", f"Pipeline failed with error: {result.get('error')}"
    
    briefing_path = f"D:\\OBSIDIAN VAULT\\Daily_Briefings\\Briefing_{result['date']}.md"
    assert os.path.exists(briefing_path), "Obsidian briefing markdown not found!"
    
    print(f" -> SUCCESS: Morning pipeline executed. Briefing saved at: {briefing_path}")
    print("=" * 70)
    print("OPERATIONAL LAYER v1 VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_operational_runner()