"""
Power BI Backtest Exporter.
Serializes backtest results and trade attribution records into canonical CSV format 
within the local powerbi data cache directory.
"""
import csv
import os

class PowerBIBacktestExporter:
    def __init__(self, output_dir: str = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_trades(self, strategy_name: str, trades: list[dict]) -> str:
        file_path = os.path.join(self.output_dir, f"backtest_trades_{strategy_name}.csv")
        fieldnames = ["strategy_id", "symbol", "direction", "entry_time", "entry_price", "exit_time", "exit_price", "reason", "pnl"]
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for trade in trades:
                writer.writerow(trade)
                
        return file_path
