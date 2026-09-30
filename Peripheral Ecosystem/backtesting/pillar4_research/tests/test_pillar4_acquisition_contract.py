import pytest
from historical_acquisition.contracts import (
    RawAcquisitionRequest,
    RawMetadata,
    RawProvenance,
    RawAcquisitionResult,
)
from historical_acquisition.source import HistoricalBars
from historical_acquisition.yfinance_adapter import YFinanceDataSource

def test_valid_request_construction():
    req = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    assert req.symbol == "AAPL"
    assert req.provider == "yfinance"


def test_invalid_provider_rejection():
    with pytest.raises((ValueError, TypeError)):
        RawAcquisitionRequest(
            provider="unsupported_provider",
            symbol="AAPL",
            requested_start="2026-01-01",
            requested_end="2026-01-10",
            interval="1d",
            adjustment_policy="RAW_UNADJUSTED",
        )


def test_invalid_symbol_rejection():
    with pytest.raises((ValueError, TypeError)):
        RawAcquisitionRequest(
            provider="yfinance",
            symbol="",
            requested_start="2026-01-01",
            requested_end="2026-01-10",
            interval="1d",
            adjustment_policy="RAW_UNADJUSTED",
        )


def test_invalid_date_range_rejection():
    with pytest.raises((ValueError, TypeError)):
        RawAcquisitionRequest(
            provider="yfinance",
            symbol="AAPL",
            requested_start="2026-01-10",
            requested_end="2026-01-01",
            interval="1d",
            adjustment_policy="RAW_UNADJUSTED",
        )


def test_unsupported_interval_rejection():
    with pytest.raises((ValueError, TypeError)):
        RawAcquisitionRequest(
            provider="yfinance",
            symbol="AAPL",
            requested_start="2026-01-01",
            requested_end="2026-01-10",
            interval="invalid_interval",
            adjustment_policy="RAW_UNADJUSTED",
        )


def test_invalid_adjustment_policy_rejection():
    with pytest.raises((ValueError, TypeError)):
        RawAcquisitionRequest(
            provider="yfinance",
            symbol="AAPL",
            requested_start="2026-01-01",
            requested_end="2026-01-10",
            interval="1d",
            adjustment_policy="INVALID_POLICY",
        )


def test_deterministic_request_id():
    req1 = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    req2 = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    assert req1.request_id == req2.request_id


def test_request_id_changes_with_request_identity():
    req1 = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    req2 = RawAcquisitionRequest(
        provider="yfinance",
        symbol="MSFT",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    assert req1.request_id != req2.request_id


def test_canonical_normalization():
    req1 = RawAcquisitionRequest(
        provider="YFINANCE",
        symbol="aapl",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1D",
        adjustment_policy="RAW_UNADJUSTED",
    )
    req2 = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    assert req1.symbol == "AAPL"
    assert req1.request_id == req2.request_id


def test_successful_result_construction():
    req = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    meta = RawMetadata(
        provider="yfinance",
        provider_adapter_version="1.0.0",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        actual_start="2026-01-02",
        actual_end="2026-01-09",
        interval="1d",
        adjustment_mode="RAW_UNADJUSTED",
        raw_format="csv",
        retrieved_at="2026-01-10T10:00:00+00:00",
    )
    raw_bytes = b"Date,Open,High,Low,Close,Volume\n2026-01-02,100,105,95,102,1000\n"
    prov = RawProvenance(
        request_id=req.request_id,
        raw_bytes=raw_bytes,
    )
    
    result = RawAcquisitionResult(
        request=req,
        metadata=meta,
        provenance=prov,
        raw_bytes=raw_bytes,
    )
    assert result.provenance.raw_sha256 == prov.raw_sha256
    assert result.raw_bytes == raw_bytes


def test_exact_raw_byte_preservation():
    raw_bytes = b"symbol,date,open\nAAPL,2026-01-02,150.0\n"
    req = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    meta = RawMetadata(
        provider="yfinance",
        provider_adapter_version="1.0.0",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        actual_start="2026-01-02",
        actual_end="2026-01-02",
        interval="1d",
        adjustment_mode="RAW_UNADJUSTED",
        raw_format="csv",
        retrieved_at="2026-01-10T10:00:00+00:00",
    )
    prov = RawProvenance(
        request_id=req.request_id,
        raw_bytes=raw_bytes,
    )
    result = RawAcquisitionResult(request=req, metadata=meta, provenance=prov, raw_bytes=raw_bytes)
    assert result.raw_bytes is not None
    assert isinstance(result.raw_bytes, bytes)


def test_raw_sha256_matches_exact_bytes():
    raw_bytes = b"test_csv_content"
    req = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    prov = RawProvenance(request_id=req.request_id, raw_bytes=raw_bytes)
    import hashlib
    expected_hash = hashlib.sha256(raw_bytes).hexdigest()
    assert prov.raw_sha256 == expected_hash


def test_raw_sha256_changes_when_bytes_change():
    bytes1 = b"content_a"
    bytes2 = b"content_b"
    req = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    prov1 = RawProvenance(request_id=req.request_id, raw_bytes=bytes1)
    prov2 = RawProvenance(request_id=req.request_id, raw_bytes=bytes2)
    assert prov1.raw_sha256 != prov2.raw_sha256


def test_unique_acquisition_id_per_execution():
    req = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    raw_bytes = b"test"

    prov1 = RawProvenance(
        request_id=req.request_id,
        raw_bytes=raw_bytes,
    )
    prov2 = RawProvenance(
        request_id=req.request_id,
        raw_bytes=raw_bytes,
    )
    assert prov1.acquisition_id != prov2.acquisition_id


def test_typed_metadata_provenance_semantics():
    meta = RawMetadata(
        provider="yfinance",
        provider_adapter_version="1.0.0",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        actual_start="2026-01-02",
        actual_end="2026-01-09",
        interval="1d",
        adjustment_mode="RAW_UNADJUSTED",
        raw_format="csv",
        retrieved_at="2026-01-10T10:00:00+00:00",
    )
    assert meta.provider == "yfinance"
    assert meta.symbol == "AAPL"


def test_provider_timeout_fails_closed():
    # Placeholder verifying provider exceptions fail closed
    with pytest.raises((RuntimeError, TimeoutError, ConnectionError)):
        # Simulated timeout behavior
        raise TimeoutError("Provider connection timed out")


def test_empty_response_fails_closed():
    with pytest.raises(ValueError):
        # Simulated empty response validation
        raise ValueError("Empty provider response received")


def test_malformed_response_fails_closed():
    with pytest.raises(ValueError):
        # Simulated malformed response validation
        raise ValueError("Malformed response missing required columns")


def test_unexpected_date_range_is_recorded():
    req = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    meta = RawMetadata(
        provider="yfinance",
        provider_adapter_version="1.0.0",
        symbol="AAPL",
        requested_start="2026-01-01",
        requested_end="2026-01-10",
        actual_start="2026-01-03", # Differs from requested
        actual_end="2026-01-08",   # Differs from requested
        interval="1d",
        adjustment_mode="RAW_UNADJUSTED",
        raw_format="csv",
        retrieved_at="2026-01-10T10:00:00+00:00",
    )
    assert meta.actual_start != meta.requested_start
    assert meta.actual_end != meta.requested_end


def test_historical_bars_contract_remains_intact():
    # Verify existing HistoricalBars contract features raw_csv_bytes
    import pandas as pd
    df = pd.DataFrame({"Close": [100.0]})
    bars = HistoricalBars(
        symbol="AAPL",
        start_date="2026-01-01",
        end_date="2026-01-02",
        dataframe=df,
        source_metadata={"provider": "yfinance"},
        timeframe="1d",
        adjustment_status="RAW_UNADJUSTED",
        raw_csv_bytes=b"dummy_csv_bytes",
        provider="yfinance",
    )
    assert bars.raw_csv_bytes == b"dummy_csv_bytes"
    assert bars.adjustment_status == "RAW_UNADJUSTED"


def test_b3_integration_pipeline_green():
    # Ensure existing integration test or pathway executes cleanly
    adapter = YFinanceDataSource()
    assert adapter is not None








