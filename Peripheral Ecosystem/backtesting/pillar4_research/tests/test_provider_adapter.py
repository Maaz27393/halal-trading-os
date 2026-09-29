import pytest
import pandas as pd
from unittest.mock import MagicMock

def test_yfinance_adapter_successful_response():
    from historical_acquisition.yfinance_adapter import YFinanceDataSource
    
    mock_downloader = MagicMock()
    mock_df = pd.DataFrame({
        "Open": [100.0, 101.0],
        "High": [102.0, 103.0],
        "Low": [99.0, 100.0],
        "Close": [101.0, 102.0],
        "Volume": [1000, 1500]
    }, index=pd.to_datetime(["2026-01-01", "2026-01-02"]))
    
    mock_downloader.return_value = mock_df
    
    adapter = YFinanceDataSource(downloader=mock_downloader)
    bars = adapter.fetch_daily("AAPL", "2026-01-01", "2026-01-02")
    
    assert bars.symbol == "AAPL"
    assert bars.start_date == "2026-01-01"
    assert bars.end_date == "2026-01-02"
    assert not bars.dataframe.empty
    assert isinstance(bars.raw_csv_bytes, bytes)
    assert bars.provider == "yfinance"
    assert bars.adjustment_status == "RAW_UNADJUSTED"
    assert bars.timeframe == "1D"

def test_yfinance_adapter_flattens_multiindex():
    from historical_acquisition.yfinance_adapter import YFinanceDataSource

    mock_downloader = MagicMock()

    # Realistic yfinance-style MultiIndex OHLCV response
    arrays = [
        ["Open", "High", "Low", "Close", "Volume"],
        ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
    ]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=["Price", "Ticker"])

    mock_df = pd.DataFrame(
        [[100.0, 102.0, 99.0, 101.0, 1000]],
        index=pd.to_datetime(["2026-01-01"]),
        columns=index,
    )

    mock_downloader.return_value = mock_df

    adapter = YFinanceDataSource(downloader=mock_downloader)

    bars = adapter.fetch_daily(
        "AAPL",
        "2026-01-01",
        "2026-01-02",
    )

    assert list(bars.dataframe.columns) == [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    assert bars.dataframe.iloc[0].to_dict() == {
        "Date": "2026-01-01",
        "Open": 100.0,
        "High": 102.0,
        "Low": 99.0,
        "Close": 101.0,
        "Volume": 1000,
    }

def test_yfinance_adapter_provider_exception_fails_closed():
    from historical_acquisition.yfinance_adapter import YFinanceDataSource
    
    mock_downloader = MagicMock()
    mock_downloader.side_effect = Exception("Network timeout")
    
    adapter = YFinanceDataSource(downloader=mock_downloader)
    with pytest.raises(RuntimeError):
        adapter.fetch_daily("AAPL", "2026-01-01", "2026-01-02")

def test_yfinance_adapter_empty_response_fails_closed():
    from historical_acquisition.yfinance_adapter import YFinanceDataSource
    
    mock_downloader = MagicMock()
    mock_downloader.return_value = pd.DataFrame()
    
    adapter = YFinanceDataSource(downloader=mock_downloader)
    with pytest.raises(ValueError):
        adapter.fetch_daily("AAPL", "2026-01-01", "2026-01-02")

def test_yfinance_adapter_missing_columns_fails_closed():
    from historical_acquisition.yfinance_adapter import YFinanceDataSource
    
    mock_downloader = MagicMock()
    mock_df = pd.DataFrame({
        "BadCol": [1.0, 2.0]
    }, index=pd.to_datetime(["2026-01-01", "2026-01-02"]))
    mock_downloader.return_value = mock_df
    
    adapter = YFinanceDataSource(downloader=mock_downloader)
    with pytest.raises(ValueError):
        adapter.fetch_daily("AAPL", "2026-01-01", "2026-01-02")

def test_yfinance_adapter_preserves_symbol_and_dates():
    from historical_acquisition.yfinance_adapter import YFinanceDataSource
    
    mock_downloader = MagicMock()
    mock_df = pd.DataFrame({
        "Open": [100.0], "High": [102.0], "Low": [99.0], "Close": [101.0], "Volume": [1000]
    }, index=pd.to_datetime(["2026-01-01"]))
    mock_downloader.return_value = mock_df
    
    adapter = YFinanceDataSource(downloader=mock_downloader)
    bars = adapter.fetch_daily("TSLA", "2026-01-01", "2026-01-01")
    
    assert bars.symbol == "TSLA"
    assert bars.start_date == "2026-01-01"
    assert bars.end_date == "2026-01-01"

def test_yfinance_adapter_raw_csv_bytes_deterministic():
    from historical_acquisition.yfinance_adapter import YFinanceDataSource
    
    mock_downloader = MagicMock()
    mock_df = pd.DataFrame({
        "Open": [100.0], "High": [102.0], "Low": [99.0], "Close": [101.0], "Volume": [1000]
    }, index=pd.to_datetime(["2026-01-01"]))
    mock_downloader.return_value = mock_df
    
    adapter1 = YFinanceDataSource(downloader=mock_downloader)
    bars1 = adapter1.fetch_daily("AAPL", "2026-01-01", "2026-01-01")
    
    adapter2 = YFinanceDataSource(downloader=mock_downloader)
    bars2 = adapter2.fetch_daily("AAPL", "2026-01-01", "2026-01-01")
    
    assert bars1.raw_csv_bytes == bars2.raw_csv_bytes

def test_yfinance_adapter_forces_auto_adjust_false():
    from historical_acquisition.yfinance_adapter import YFinanceDataSource
    
    mock_downloader = MagicMock()
    mock_df = pd.DataFrame({
        "Open": [100.0], "High": [102.0], "Low": [99.0], "Close": [101.0], "Volume": [1000]
    }, index=pd.to_datetime(["2026-01-01"]))
    mock_downloader.return_value = mock_df
    
    adapter = YFinanceDataSource(downloader=mock_downloader)
    adapter.fetch_daily("AAPL", "2026-01-01", "2026-01-01")
    
    _, kwargs = mock_downloader.call_args
    assert kwargs.get("auto_adjust") is False
