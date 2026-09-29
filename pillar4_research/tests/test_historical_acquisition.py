import pytest
import pandas as pd
from pathlib import Path
from pillar4_research.src.historical_acquisition.source import HistoricalDataSource, HistoricalBars
from pillar4_research.src.historical_acquisition.staging import StagingManager
try:
    from pillar4_research.src.historical_acquisition.validation import AcquisitionValidator
except ImportError:
    AcquisitionValidator = None

class MockDataSource(HistoricalDataSource):
    def __init__(self, should_fail: bool = False, empty_response: bool = False, duplicate_dates: bool = False):
        self.should_fail = should_fail
        self.empty_response = empty_response
        self.duplicate_dates = duplicate_dates

    def fetch_daily(self, symbol: str, start_date: str, end_date: str) -> HistoricalBars:
        if self.should_fail:
            raise ConnectionError("Upstream historical data source unavailable.")
        if self.empty_response:
            return HistoricalBars(symbol=symbol, start_date=start_date, end_date=end_date, dataframe=pd.DataFrame())
        
        dates = [start_date, end_date]
        if self.duplicate_dates:
            dates = [start_date, start_date]

        df = pd.DataFrame({
            "Date": dates,
            "Open": [100.0, 102.0],
            "High": [105.0, 106.0],
            "Low": [98.0, 101.0],
            "Close": [102.0, 104.0],
            "Volume": [10000, 15000]
        })
        return HistoricalBars(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            dataframe=df,
            source_metadata={"provider": "mock", "retrieved_at": "2026-09-29T18:00:00"}
        )

def test_s41_t01_source_returns_canonical_observations():
    source = MockDataSource()
    bars = source.fetch_daily("RELIANCE", "2025-01-01", "2025-01-02")
    assert isinstance(bars, HistoricalBars)
    assert not bars.dataframe.empty

def test_s41_t02_requested_symbol_preserved():
    source = MockDataSource()
    bars = source.fetch_daily("TCS", "2025-01-01", "2025-01-02")
    assert bars.symbol == "TCS"

def test_s41_t03_requested_date_range_preserved():
    source = MockDataSource()
    bars = source.fetch_daily("INFY", "2025-01-01", "2025-01-31")
    assert bars.start_date == "2025-01-01"
    assert bars.end_date == "2025-01-31"

def test_s41_t04_required_ohlcv_fields_present():
    source = MockDataSource()
    bars = source.fetch_daily("RELIANCE", "2025-01-01", "2025-01-02")
    expected_cols = {"Date", "Open", "High", "Low", "Close", "Volume"}
    assert expected_cols.issubset(bars.dataframe.columns)

def test_s41_t05_acquisition_failure_is_fail_closed():
    source = MockDataSource(should_fail=True)
    with pytest.raises(ConnectionError):
        source.fetch_daily("RELIANCE", "2025-01-01", "2025-01-02")

def test_s41_t06_empty_historical_response_rejected():
    if AcquisitionValidator is None:
        pytest.fail("AcquisitionValidator not implemented (RED state)")
    source = MockDataSource(empty_response=True)
    bars = source.fetch_daily("RELIANCE", "2025-01-01", "2025-01-02")
    with pytest.raises(ValueError, match="empty historical dataset"):
        AcquisitionValidator.validate(bars)

def test_s41_t07_duplicate_observations_rejected():
    if AcquisitionValidator is None:
        pytest.fail("AcquisitionValidator not implemented (RED state)")
    source = MockDataSource(duplicate_dates=True)
    bars = source.fetch_daily("RELIANCE", "2025-01-01", "2025-01-01")
    with pytest.raises(ValueError, match="Duplicate dates detected"):
        AcquisitionValidator.validate(bars)

def test_s41_t08_staging_prevents_silent_overwrite(tmp_path):
    manager = StagingManager(tmp_path)
    source = MockDataSource()
    bars = source.fetch_daily("RELIANCE", "2025-01-01", "2025-01-02")
    
    path1 = manager.stage_bars(bars, overwrite=False)
    assert path1.exists()

    with pytest.raises(FileExistsError):
        manager.stage_bars(bars, overwrite=False)

    path2 = manager.stage_bars(bars, overwrite=True)
    assert path2.exists()

def test_s41_t09_raw_acquisition_separate_from_backtest_dataset():
    source = MockDataSource()
    bars = source.fetch_daily("RELIANCE", "2025-01-01", "2025-01-02")
    assert not hasattr(bars, "dataset_sha")

def test_s41_t10_staged_artifact_matches_p43_input_contract(tmp_path):
    if AcquisitionValidator is None:
        pytest.fail("AcquisitionValidator not implemented (RED state)")
    manager = StagingManager(tmp_path)
    source = MockDataSource()
    bars = source.fetch_daily("RELIANCE", "2025-01-01", "2025-01-02")
    AcquisitionValidator.validate(bars)
    staged_path = manager.stage_bars(bars)
    
    loaded_df = pd.read_csv(staged_path)
    required_p43_columns = {"Date", "Open", "High", "Low", "Close", "Volume"}
    assert required_p43_columns.issubset(loaded_df.columns)
    assert len(loaded_df) == 2
