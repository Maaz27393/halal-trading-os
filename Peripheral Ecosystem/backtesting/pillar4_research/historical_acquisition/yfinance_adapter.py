import io
import pandas as pd
from .source import ALLOWED_ADJUSTMENT_STATUSES, HistoricalBars, HistoricalDataSource

class YFinanceDataSource(HistoricalDataSource):
    def __init__(self, adjustment_status: str = "RAW_UNADJUSTED", downloader=None):
        if adjustment_status not in ALLOWED_ADJUSTMENT_STATUSES:
            raise ValueError(
                f"Unsupported adjustment mode '{adjustment_status}'. "
                f"Must be one of {ALLOWED_ADJUSTMENT_STATUSES}."
            )

        self.adjustment_status = adjustment_status
        self.provider = "yfinance"

        if downloader is None:
            import yfinance as yf
            self._downloader = yf.download
        elif callable(downloader):
            self._downloader = downloader
        elif hasattr(downloader, "download") and callable(downloader.download):
            self._downloader = downloader.download
        else:
            raise TypeError(
                "downloader must expose a callable download attribute or be callable."
            )

    def fetch_daily(self, symbol: str, start_date: str, end_date: str) -> HistoricalBars:
        try:
            df = self._downloader(
                symbol,
                start=start_date,
                end=end_date,
                interval="1d",
                progress=False,
                auto_adjust=False
            )
        except Exception as exc:
            raise RuntimeError(
                f"YFinanceDataSource execution error for symbol '{symbol}': {exc}"
            ) from exc

        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            raise ValueError(
                f"Provider returned empty response for symbol '{symbol}' between {start_date} and {end_date}."
            )

        if not isinstance(df, pd.DataFrame):
            raise ValueError(
                f"Provider returned unexpected response type for '{symbol}': expected DataFrame, got {type(df)}."
            )

        if isinstance(df.columns, pd.MultiIndex):
            df = df.copy()
            df.columns = df.columns.get_level_values(0)

        required_columns = {"Open", "High", "Low", "Close", "Volume"}
        present_columns = set(df.columns)
        missing_columns = required_columns - present_columns

        if missing_columns:
            raise ValueError(
                f"Provider response missing required OHLCV columns {missing_columns}. Got: {list(df.columns)}"
            )

        df_reset = df.reset_index()
        date_column = df_reset.columns[0]
        df_reset.rename(columns={date_column: "Date"}, inplace=True)
        df_reset["Date"] = pd.to_datetime(df_reset["Date"]).dt.strftime("%Y-%m-%d")

        canonical_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        df_canonical = df_reset[canonical_columns].copy()

        csv_buffer = io.StringIO()
        df_canonical.to_csv(csv_buffer, index=False, lineterminator="\n")
        raw_csv_bytes = csv_buffer.getvalue().encode("utf-8")

        source_metadata = {
            "provider": self.provider,
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "adjustment_status": self.adjustment_status
        }

        return HistoricalBars(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            dataframe=df_canonical,
            source_metadata=source_metadata,
            timeframe="1D",
            adjustment_status=self.adjustment_status,
            raw_csv_bytes=raw_csv_bytes,
            provider=self.provider
        )


