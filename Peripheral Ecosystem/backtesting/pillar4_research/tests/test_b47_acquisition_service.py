import hashlib
from pathlib import Path

import pandas as pd
import pytest

from historical_acquisition.contracts import (
    RawAcquisitionRequest,
    RawAcquisitionResult,
)
from historical_acquisition.source import HistoricalBars
from historical_acquisition.staging import stage_raw_bars
from historical_acquisition.acquisition_service import execute_raw_acquisition


RAW_BYTES = (
    b"Date,Open,High,Low,Close,Volume\n"
    b"2026-01-02,100,105,99,104,1000000\n"
    b"2026-01-05,102,106,101,105,1200000\n"
)


class FakeHistoricalDataSource:
    """Deterministic B.3-compatible provider boundary for B.4.7 tests."""

    def __init__(self, raw_bytes: bytes = RAW_BYTES):
        self.raw_bytes = raw_bytes
        self.calls = []

    def fetch_daily(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> HistoricalBars:
        self.calls.append((symbol, start_date, end_date))

        dataframe = pd.DataFrame(
            {
                "Date": pd.to_datetime(
                    ["2026-01-02", "2026-01-05"]
                ),
                "Open": [100.0, 102.0],
                "High": [105.0, 106.0],
                "Low": [99.0, 101.0],
                "Close": [104.0, 105.0],
                "Volume": [1000000, 1200000],
            }
        ).set_index("Date")

        return HistoricalBars(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            dataframe=dataframe,
            source_metadata={"provider": "yfinance"},
            timeframe="1D",
            adjustment_status="RAW_UNADJUSTED",
            raw_csv_bytes=self.raw_bytes,
            provider="yfinance",
        )


def make_request() -> RawAcquisitionRequest:
    return RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-02",
        requested_end="2026-01-08",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )


def test_b47_service_integration_success():
    request = make_request()
    source = FakeHistoricalDataSource()

    result = execute_raw_acquisition(
        request,
        data_source=source,
    )

    assert isinstance(result, RawAcquisitionResult)
    assert result.request.request_id == request.request_id
    assert result.metadata.symbol == "AAPL"
    assert result.metadata.provider == "yfinance"
    assert result.metadata.requested_start == "2026-01-02"
    assert result.metadata.requested_end == "2026-01-08"
    assert result.metadata.actual_start == "2026-01-02"
    assert result.metadata.actual_end == "2026-01-05"
    assert result.metadata.interval == "1d"
    assert result.metadata.adjustment_mode == "RAW_UNADJUSTED"
    assert result.metadata.raw_format == "csv"

    assert result.raw_bytes == RAW_BYTES
    assert result.provenance.raw_bytes == RAW_BYTES
    assert result.provenance.raw_sha256 == hashlib.sha256(
        RAW_BYTES
    ).hexdigest()

    assert source.calls == [
        ("AAPL", "2026-01-02", "2026-01-08")
    ]


def test_b47_distinct_acquisition_ids():
    request = make_request()
    source = FakeHistoricalDataSource()

    result1 = execute_raw_acquisition(
        request,
        data_source=source,
    )
    result2 = execute_raw_acquisition(
        request,
        data_source=source,
    )

    assert result1.request.request_id == result2.request.request_id
    assert (
        result1.provenance.acquisition_id
        != result2.provenance.acquisition_id
    )


def test_b47_staging_compatibility(tmp_path: Path):
    request = make_request()
    source = FakeHistoricalDataSource()

    result = execute_raw_acquisition(
        request,
        data_source=source,
    )

    bars = source.fetch_daily(
        symbol=request.symbol,
        start_date=request.requested_start,
        end_date=request.requested_end,
    )

    staged_path = stage_raw_bars(
        bars,
        tmp_path,
    )

    assert staged_path.exists()
    assert staged_path.read_bytes() == result.raw_bytes


def test_b47_provider_failure_remains_fail_closed():
    class FailingDataSource:
        def fetch_daily(self, symbol, start_date, end_date):
            raise RuntimeError("provider unavailable")

    request = make_request()

    with pytest.raises(RuntimeError, match="provider unavailable"):
        execute_raw_acquisition(
            request,
            data_source=FailingDataSource(),
        )


def test_b47_missing_raw_bytes_fails_closed():
    class MissingRawBytesDataSource:
        def fetch_daily(self, symbol, start_date, end_date):
            dataframe = pd.DataFrame(
                {
                    "Date": pd.to_datetime(["2026-01-02"]),
                    "Open": [100.0],
                    "High": [105.0],
                    "Low": [99.0],
                    "Close": [104.0],
                    "Volume": [1000000],
                }
            ).set_index("Date")

            return HistoricalBars(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                dataframe=dataframe,
                source_metadata={"provider": "yfinance"},
                timeframe="1D",
                adjustment_status="RAW_UNADJUSTED",
                raw_csv_bytes=None,
                provider="yfinance",
            )

    request = make_request()

    with pytest.raises(
        ValueError,
        match="raw_csv_bytes",
    ):
        execute_raw_acquisition(
            request,
            data_source=MissingRawBytesDataSource(),
        )


def test_b47_normalizes_timezone_aware_timestamp_actual_range():
    import pandas as pd
    from historical_acquisition.source import HistoricalBars

    request = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-02",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )

    class TimezoneAwareFakeSource:
        def fetch_daily(self, symbol, start_date, end_date):
            df = pd.DataFrame(
                {
                    "Open": [100.0, 102.0],
                    "High": [105.0, 106.0],
                    "Low": [99.0, 101.0],
                    "Close": [104.0, 105.5],
                    "Volume": [1000000, 1200000],
                },
                index=pd.Index(
                    [
                        "2026-01-02 00:00:00-05:00",
                        "2026-01-05 00:00:00-05:00",
                    ]
                ),
            )
            return HistoricalBars(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                dataframe=df,
                source_metadata={"provider": "yfinance"},
                timeframe="1D",
                adjustment_status="RAW_UNADJUSTED",
                raw_csv_bytes=b"fake,csv,bytes",
                provider="yfinance",
            )

    result = execute_raw_acquisition(
        request,
        data_source=TimezoneAwareFakeSource(),
    )

    assert result.metadata.actual_start == "2026-01-02"
    assert result.metadata.actual_end == "2026-01-05"


def test_b47_derives_actual_range_from_date_column():
    import pandas as pd
    from historical_acquisition.source import HistoricalBars

    dataframe = pd.DataFrame(
        {
            "Date": [
                "2026-01-02",
                "2026-01-05",
                "2026-01-06",
            ],
            "Open": [100.0, 102.0, 103.0],
            "High": [105.0, 106.0, 107.0],
            "Low": [99.0, 101.0, 102.0],
            "Close": [104.0, 105.0, 106.0],
            "Volume": [1000000, 1200000, 1100000],
        }
    )

    class DateColumnFakeSource:
        def fetch_daily(self, symbol, start_date, end_date):
            return HistoricalBars(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                dataframe=dataframe,
                source_metadata={"provider": "yfinance"},
                timeframe="1D",
                adjustment_status="RAW_UNADJUSTED",
                raw_csv_bytes=b"fake,csv,bytes",
                provider="yfinance",
            )

    request = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-02",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )

    result = execute_raw_acquisition(request, data_source=DateColumnFakeSource())

    assert result.metadata.actual_start == "2026-01-02"
    assert result.metadata.actual_end == "2026-01-06"


def test_b47_fails_closed_when_actual_range_undervolumed():
    import pandas as pd
    import pytest
    from historical_acquisition.source import HistoricalBars

    # DataFrame with RangeIndex and no date column or datetime index
    dataframe = pd.DataFrame(
        {
            "Open": [100.0, 102.0],
            "Close": [104.0, 105.5],
        }
    )

    class InvalidShapeFakeSource:
        def fetch_daily(self, symbol, start_date, end_date):
            return HistoricalBars(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                dataframe=dataframe,
                source_metadata={"provider": "yfinance"},
                timeframe="1D",
                adjustment_status="RAW_UNADJUSTED",
                raw_csv_bytes=b"fake,csv,bytes",
                provider="yfinance",
            )

    request = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-02",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )

    with pytest.raises(ValueError, match="Unable to derive actual acquisition date range"):
        execute_raw_acquisition(request, data_source=InvalidShapeFakeSource())
