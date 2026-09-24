"""
Power BI Analytical Exporter (Pillar 4 - Phase C).
Serializes enriched trade attribution, strategy-level summary KPIs, and chronological 
equity curves into the three canonical CSV staging feeders for Power BI.
"""
import csv
import os

class PowerBIAnalyticsExporter:
    def __init__(self, output_dir: str = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_all(self, strategy_name: str, enriched_trades: list[dict], summary_kpis: dict, equity_curve_data: list[dict]) -> dict:
        paths = {}
        
        # 1. Export Trade Attribution Table
        trades_path = os.path.join(self.output_dir, f"backtest_trades_{strategy_name}.csv")
        if enriched_trades:
            fieldnames = list(enriched_trades[0].keys())
            with open(trades_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for trade in enriched_trades:
                    writer.writerow(trade)
        paths["trades"] = trades_path

        # 2. Export Strategy Summary KPI Table
        summary_path = os.path.join(self.output_dir, f"backtest_summary_{strategy_name}.csv")
        with open(summary_path, mode='w', newline='', encoding='utf-8') as f:
            if summary_kpis:
                writer = csv.DictWriter(f, fieldnames=list(summary_kpis.keys()))
                writer.writeheader()
                writer.writerow(summary_kpis)
        paths["summary"] = summary_path

        # 3. Export Equity Curve & Drawdown Table
        equity_path = os.path.join(self.output_dir, f"backtest_equity_curve_{strategy_name}.csv")
        if equity_curve_data:
            fieldnames = list(equity_curve_data[0].keys())
            with open(equity_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for pt in equity_curve_data:
                    writer.writerow(pt)
        paths["equity"] = equity_path

        return paths
