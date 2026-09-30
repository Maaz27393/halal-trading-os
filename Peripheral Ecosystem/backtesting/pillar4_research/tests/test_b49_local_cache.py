from __future__ import annotations

import json
from pathlib import Path
import pytest
import pandas as pd

from historical_acquisition.contracts import (
    RawAcquisitionRequest,
    RawAcquisitionResult,
    RawMetadata,
    RawProvenance,
)
from historical_acquisition.source import HistoricalBars

# Note: These imports and module will fail until historical_acquisition.cache is implemented (RED phase).
from historical_acquisition.cache import (
    LocalHistoricalCache,
    CacheIntegrityError,
    CacheConflictError,
)


class DummySource:
    def __init__(self, df: pd.DataFrame, csv_bytes: bytes = b"Date,Close\n2026-01-02,100\n"):
        self.df = df
        self.csv_bytes = csv_bytes
        self.call_count = 0

    def fetch_daily(self, symbol, start_date, end_date):
        self.call_count += 1
        return HistoricalBars(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            dataframe=self.df,
            source_metadata={"provider": "yfinance", "adapter_version": "1.0.0"},
            timeframe="1D",
            adjustment_status="RAW_UNADJUSTED",
            raw_csv_bytes=self.csv_bytes,
            provider="yfinance",
        )


@pytest.fixture
def sample_request() -> RawAcquisitionRequest:
    return RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-02",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Date": ["2026-01-02", "2026-01-05"],
        "Close": [100.0, 105.0]
    })


def test_b49_t1_deterministic_cache_key(tmp_path, sample_request):
    req1 = sample_request
    req2 = RawAcquisitionRequest(
        provider="yfinance",
        symbol="AAPL",
        requested_start="2026-01-02",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    assert req1.request_id == req2.request_id
    cache = LocalHistoricalCache(base_dir=tmp_path)
    assert cache.get_cache_key(req1) == req1.request_id


def test_b49_t2_different_request_different_key(sample_request):
    req2 = RawAcquisitionRequest(
        provider="yfinance",
        symbol="MSFT",
        requested_start="2026-01-02",
        requested_end="2026-01-10",
        interval="1d",
        adjustment_policy="RAW_UNADJUSTED",
    )
    assert sample_request.request_id != req2.request_id


def test_b49_t3_cache_miss_persists_artifact_and_manifest(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")

    result = cache.get_or_execute(sample_request, data_source=source)
    assert result is not None
    assert source.call_count == 1

    entry_dir = tmp_path / sample_request.request_id
    assert entry_dir.exists()
    assert (entry_dir / "raw_data.csv").exists()
    assert (entry_dir / "manifest.json").exists()


def test_b49_t4_valid_cache_hit_avoids_reacquisition(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")

    # First call: Cache miss -> executes
    res1 = cache.get_or_execute(sample_request, data_source=source)
    assert source.call_count == 1

    # Second call: Cache hit -> retrieves from disk without calling source
    res2 = cache.get_or_execute(sample_request, data_source=source)
    assert source.call_count == 1  # Call count must not increment!
    assert res2.raw_bytes == res1.raw_bytes
    assert res2.provenance.acquisition_id == res1.provenance.acquisition_id


def test_b49_t5_hit_preserves_complete_provenance(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")

    res1 = cache.get_or_execute(sample_request, data_source=source)
    res2 = cache.get_or_execute(sample_request, data_source=source)

    # Verify complete identity & provenance preservation
    assert res2.request == res1.request
    assert res2.provenance.acquisition_id == res1.provenance.acquisition_id
    assert res2.provenance.raw_sha256 == res1.provenance.raw_sha256
    assert res2.metadata.actual_start == res1.metadata.actual_start
    assert res2.metadata.actual_end == res1.metadata.actual_end
    assert res2.metadata.provider == res1.metadata.provider
    assert res2.metadata.provider_adapter_version == res1.metadata.provider_adapter_version
    assert res2.metadata.symbol == res1.metadata.symbol
    assert res2.metadata.requested_start == res1.metadata.requested_start
    assert res2.metadata.requested_end == res1.metadata.requested_end
    assert res2.metadata.interval == res1.metadata.interval
    assert res2.metadata.adjustment_mode == res1.metadata.adjustment_mode
    assert res2.metadata.raw_format == res1.metadata.raw_format
    assert res2.raw_bytes == res1.raw_bytes


def test_b49_t6_mutated_raw_data_raises_integrity_error(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")
    cache.get_or_execute(sample_request, data_source=source)

    # Tamper with raw data bytes
    raw_file = tmp_path / sample_request.request_id / "raw_data.csv"
    raw_file.write_bytes(b"CORRUPTED BYTES")

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t7_missing_manifest_raises_integrity_error(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")
    cache.get_or_execute(sample_request, data_source=source)

    # Remove manifest.json
    manifest_file = tmp_path / sample_request.request_id / "manifest.json"
    manifest_file.unlink()

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t8_missing_raw_artifact_raises_integrity_error(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")
    cache.get_or_execute(sample_request, data_source=source)

    # Remove raw_data.csv
    raw_file = tmp_path / sample_request.request_id / "raw_data.csv"
    raw_file.unlink()

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t9_manifest_identity_mismatch_raises_integrity_error(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")
    cache.get_or_execute(sample_request, data_source=source)

    # Tamper manifest symbol
    manifest_path = tmp_path / sample_request.request_id / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["symbol"] = "TAMPERED_SYMBOL"
    manifest_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t10_explicit_conflicting_persistence_raises_conflict_error(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source1 = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")
    res1 = cache.get_or_execute(sample_request, data_source=source1)

    # Create a conflicting result with different raw bytes / hash for the same request
    source2 = DummySource(sample_df, b"Date,Close\n2026-01-02,999\n")
    res2_alt = cache.execute_and_build_result(sample_request, data_source=source2)

    with pytest.raises(CacheConflictError):
        cache.store(res2_alt)

    # Verify original remains intact
    res_verify = cache.get_or_execute(sample_request, data_source=source1)
    assert b"100" in res_verify.raw_bytes
    assert b"999" not in res_verify.raw_bytes


def test_b49_t11_incomplete_entry_raises_integrity_error_no_acquisition(tmp_path, sample_request, sample_df):
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")
    cache.get_or_execute(sample_request, data_source=source)

    # Remove manifest to create incomplete/corrupt entry state
    manifest_path = tmp_path / sample_request.request_id / "manifest.json"
    manifest_path.unlink()

    source_fresh = DummySource(sample_df, b"Date,Close\n2026-01-02,100\n")

    # Incomplete entry must fail closed with CacheIntegrityError and MUST NOT trigger source acquisition
    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source_fresh)

    assert source_fresh.call_count == 0


def test_b49_t12_cached_bytes_exactly_equal_original(tmp_path, sample_request, sample_df):
    original_bytes = b"Date,Close\n2026-01-02,100.25\n2026-01-05,101.50\n"
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(sample_df, original_bytes)

    res1 = cache.get_or_execute(sample_request, data_source=source)
    res2 = cache.get_or_execute(sample_request, data_source=source)

    assert res2.raw_bytes == original_bytes
    assert res1.raw_bytes == original_bytes


# ==========================================
# B.4.9 INTEGRITY CORRUPTION MATRIX (T13-T18)
# ==========================================

def test_b49_t13_raw_sha256_mismatch_fails_closed(
    tmp_path, sample_request, sample_df
):
    """T13: Mutated raw artifact must fail closed on SHA-256 mismatch."""
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(
        sample_df,
        b"Date,Close\n2026-01-02,100\n",
    )

    cache.get_or_execute(sample_request, data_source=source)

    raw_file = tmp_path / sample_request.request_id / "raw_data.csv"
    raw_file.write_bytes(b"TAMPERED DATA")

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t14_malformed_manifest_provenance_fails_closed(
    tmp_path, sample_request, sample_df
):
    """T14: Invalid acquisition provenance must fail closed."""
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(
        sample_df,
        b"Date,Close\n2026-01-02,100\n",
    )

    cache.get_or_execute(sample_request, data_source=source)

    manifest_file = (
        tmp_path / sample_request.request_id / "manifest.json"
    )
    manifest_data = json.loads(
        manifest_file.read_text(encoding="utf-8")
    )

    # Corrupt a mandatory provenance field.
    manifest_data["acquisition_id"] = ""

    manifest_file.write_text(
        json.dumps(manifest_data),
        encoding="utf-8",
    )

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t15_invalid_actual_date_range_fails_closed(
    tmp_path, sample_request, sample_df
):
    """T15: Invalid actual acquisition dates must fail closed."""
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(
        sample_df,
        b"Date,Close\n2026-01-02,100\n",
    )

    cache.get_or_execute(sample_request, data_source=source)

    manifest_file = (
        tmp_path / sample_request.request_id / "manifest.json"
    )
    manifest_data = json.loads(
        manifest_file.read_text(encoding="utf-8")
    )

    # Make the actual range internally invalid.
    manifest_data["actual_start"] = "2026-01-10"
    manifest_data["actual_end"] = "2026-01-02"

    manifest_file.write_text(
        json.dumps(manifest_data),
        encoding="utf-8",
    )

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t16_malformed_json_fails_closed(
    tmp_path, sample_request, sample_df
):
    """T16: Malformed manifest JSON must fail closed."""
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(
        sample_df,
        b"Date,Close\n2026-01-02,100\n",
    )

    cache.get_or_execute(sample_request, data_source=source)

    manifest_file = (
        tmp_path / sample_request.request_id / "manifest.json"
    )

    manifest_file.write_text(
        '{"request_id":',
        encoding="utf-8",
    )

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t17_directory_request_id_mismatch_fails_closed(
    tmp_path, sample_request, sample_df
):
    """T17: Directory identity must match manifest request identity."""
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(
        sample_df,
        b"Date,Close\n2026-01-02,100\n",
    )

    cache.get_or_execute(sample_request, data_source=source)

    original_dir = tmp_path / sample_request.request_id
    mismatched_dir = tmp_path / ("0" * 64)

    original_dir.rename(mismatched_dir)

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)


def test_b49_t18_manifest_request_fields_reconstruct_different_request_id(
    tmp_path, sample_request, sample_df
):
    """T18: Manifest request fields must reconstruct the stored request_id."""
    cache = LocalHistoricalCache(base_dir=tmp_path)
    source = DummySource(
        sample_df,
        b"Date,Close\n2026-01-02,100\n",
    )

    cache.get_or_execute(sample_request, data_source=source)

    manifest_file = (
        tmp_path / sample_request.request_id / "manifest.json"
    )
    manifest_data = json.loads(
        manifest_file.read_text(encoding="utf-8")
    )

    # Change an identity-bearing request field without changing
    # the directory/storage key.
    manifest_data["symbol"] = "MSFT"

    manifest_file.write_text(
        json.dumps(manifest_data),
        encoding="utf-8",
    )

    with pytest.raises(CacheIntegrityError):
        cache.get_or_execute(sample_request, data_source=source)
