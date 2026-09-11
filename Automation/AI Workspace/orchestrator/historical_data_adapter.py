import time
from typing import List, Dict, Any, Generator, Union

class HistoricalDataAdapter:
    """
    Phase 10A: Historical Data Adapter
    Transforms standard OHLCV historical datasets into normalized live-candle feeds
    compatible with Phase 9 Paper Trading Harness and Phase 7 Strategy Skills.
    Pure-Python native with optional DataFrame support.
    """
    def __init__(self, default_spread_pct: float = 0.05):
        self.default_spread_pct = default_spread_pct

    def normalize_candles(self, raw_records: Union[List[Dict[str, Any]], Any], ticker: str) -> List[Dict[str, Any]]:
        """
        Converts a list of dicts or DataFrame containing standard OHLCV keys/columns
        into an ordered sequence of standard candle dictionaries.
        """
        if hasattr(raw_records, "to_dict"):
            records = raw_records.to_dict(orient="records")
        elif isinstance(raw_records, list):
            records = raw_records
        else:
            records = list(raw_records)

        candles = []
        for row in records:
            clean_row = {str(k).lower().strip(): v for k, v in row.items()}

            required = {"open", "high", "low", "close", "volume"}
            if not required.issubset(set(clean_row.keys())):
                missing = required - set(clean_row.keys())
                raise ValueError(f"Missing required OHLCV keys: {missing}")

            close_p = float(clean_row["close"])
            spread = close_p * (self.default_spread_pct / 100.0)

            bid = float(clean_row["bid"]) if "bid" in clean_row and clean_row["bid"] is not None else round(close_p - (spread / 2.0), 2)
            ask = float(clean_row["ask"]) if "ask" in clean_row and clean_row["ask"] is not None else round(close_p + (spread / 2.0), 2)

            ts = int(clean_row.get("timestamp_epoch", time.time()))

            candle = {
                "ticker": ticker.upper(),
                "open": float(clean_row["open"]),
                "high": float(clean_row["high"]),
                "low": float(clean_row["low"]),
                "close": close_p,
                "volume": int(clean_row["volume"]),
                "bid": bid,
                "ask": ask,
                "timestamp_epoch": ts
            }
            candles.append(candle)

        return sorted(candles, key=lambda x: x["timestamp_epoch"])

    def create_multi_symbol_feed(self, datasets: Dict[str, Union[List[Dict[str, Any]], Any]]) -> List[Dict[str, Any]]:
        """Combines multiple historical symbol datasets into a single chronological tick stream."""
        all_candles = []
        for ticker, data in datasets.items():
            normalized = self.normalize_candles(data, ticker)
            all_candles.extend(normalized)

        return sorted(all_candles, key=lambda x: x["timestamp_epoch"])

    def stream_ticks(self, candle_feed: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        """Yields sequential historical ticks to simulate real-time socket updates."""
        for candle in candle_feed:
            yield candle
