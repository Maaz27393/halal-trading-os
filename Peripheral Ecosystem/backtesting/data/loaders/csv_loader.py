"""
Canonical CSV OHLCV Loader.
Ingests historical data from local staging cache and maps them to OHLCVBar contracts.
Robustly handles UTF-8 BOM headers and whitespace.
"""
import csv
from datetime import datetime
from backtesting.contracts.ohlcv import OHLCVBar

class CSVOHLCVLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_bars(self, symbol: str) -> list[OHLCVBar]:
        bars = []
        with open(self.file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize keys by stripping whitespace and BOM if present
                clean_row = {k.strip().lstrip('\ufeff'): v for k, v in row.items()}
                row_symbol = clean_row.get('Symbol', symbol)
                
                if row_symbol == symbol or not symbol:
                    bar = OHLCVBar(
                        timestamp=datetime.strptime(clean_row['Timestamp'], '%Y-%m-%d %H:%M:%S'),
                        symbol=row_symbol,
                        open=float(clean_row['Open']),
                        high=float(clean_row['High']),
                        low=float(clean_row['Low']),
                        close=float(clean_row['Close']),
                        volume=float(clean_row.get('Volume', 0.0))
                    )
                    bars.append(bar)
        return bars
