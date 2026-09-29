

import json
import hashlib
from datetime import datetime, timezone
from historical_acquisition.qualification import QualificationManager, QualificationManifest

def test_s41_a01_manifest_required_fields(tmp_path):
    csv_path = tmp_path / "raw.csv"
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n", encoding="utf-8")
    
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path,
        source_identity="RELIANCE_1D_RAW",
        provider="test_provider",
        symbol="RELIANCE",
        timeframe="1D",
        requested_start="2025-01-01",
        requested_end="2025-01-05",
        adjustment_status="RAW_UNADJUSTED",
        calendar_identity="NSE_EQUITY_DAILY",
        calendar_sha256="abc123sha"
    )
    
    assert manifest.source_identity == "RELIANCE_1D_RAW"
    assert manifest.provider == "test_provider"
    assert manifest.symbol == "RELIANCE"
    assert manifest.timeframe == "1D"
    assert manifest.requested_start == "2025-01-01"
    assert manifest.requested_end == "2025-01-05"
    assert manifest.actual_first_date == "2025-01-01"
    assert manifest.actual_last_date == "2025-01-01"
    assert manifest.row_count == 1
    assert manifest.adjustment_status == "RAW_UNADJUSTED"
    assert manifest.calendar_identity == "NSE_EQUITY_DAILY"
    assert manifest.calendar_sha256 == "abc123sha"
    assert len(manifest.raw_sha256) == 64

def test_s41_a03_raw_sha_equals_exact_bytes(tmp_path):
    csv_path = tmp_path / "raw.csv"
    raw_content = b"Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n"
    csv_path.write_bytes(raw_content)
    
    expected_hash = hashlib.sha256(raw_content).hexdigest()
    
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path,
        source_identity="RELIANCE_1D_RAW",
        provider="test_provider",
        symbol="RELIANCE",
        timeframe="1D",
        requested_start="2025-01-01",
        requested_end="2025-01-05",
        adjustment_status="RAW_UNADJUSTED",
        calendar_identity="NSE_EQUITY_DAILY",
        calendar_sha256="abc123sha"
    )
    
    assert manifest.raw_sha256 == expected_hash

def test_s41_a04_one_byte_mutation_fails(tmp_path):
    csv_path = tmp_path / "raw.csv"
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n", encoding="utf-8")
    
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path,
        source_identity="RELIANCE_1D_RAW",
        provider="test_provider",
        symbol="RELIANCE",
        timeframe="1D",
        requested_start="2025-01-01",
        requested_end="2025-01-05",
        adjustment_status="RAW_UNADJUSTED",
        calendar_identity="NSE_EQUITY_DAILY",
        calendar_sha256="abc123sha"
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest.to_dict()))
    
    # Mutate CSV byte
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,103,1000\n", encoding="utf-8")
    
    valid, err = QualificationManager.verify_sidecar(csv_path, manifest_path)
    assert not valid
    assert "hash mismatch" in err.lower()

def test_s41_a10_missing_manifest_rejected(tmp_path):
    csv_path = tmp_path / "raw.csv"
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n", encoding="utf-8")
    manifest_path = tmp_path / "nonexistent.json"
    
    valid, err = QualificationManager.verify_sidecar(csv_path, manifest_path)
    assert not valid

def test_s41_a12_retrieved_at_provenance_independence(tmp_path):
    csv_path = tmp_path / "raw.csv"
    raw_content = b"Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n"
    csv_path.write_bytes(raw_content)
    
    m1 = QualificationManager.generate_manifest(
        csv_path=csv_path, source_identity="X", provider="P", symbol="S", timeframe="1D",
        requested_start="2025-01-01", requested_end="2025-01-05", adjustment_status="RAW_UNADJUSTED",
        calendar_identity="CAL", calendar_sha256="HASH"
    )
    m2 = QualificationManager.generate_manifest(
        csv_path=csv_path, source_identity="X", provider="P", symbol="S", timeframe="1D",
        requested_start="2025-01-01", requested_end="2025-01-05", adjustment_status="RAW_UNADJUSTED",
        calendar_identity="CAL", calendar_sha256="HASH"
    )
    
    # Same raw bytes must produce identical raw_sha256 even if timestamps differ slightly
    assert m1.raw_sha256 == m2.raw_sha256


import json
import hashlib
from datetime import datetime, timezone
from historical_acquisition.qualification import QualificationManager, QualificationManifest

def test_s41_a01_manifest_required_fields(tmp_path):
    csv_path = tmp_path / "raw.csv"
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n", encoding="utf-8")
    
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path,
        source_identity="RELIANCE_1D_RAW",
        provider="test_provider",
        symbol="RELIANCE",
        timeframe="1D",
        requested_start="2025-01-01",
        requested_end="2025-01-05",
        adjustment_status="RAW_UNADJUSTED",
        calendar_identity="NSE_EQUITY_DAILY",
        calendar_sha256="abc123sha"
    )
    
    assert manifest.source_identity == "RELIANCE_1D_RAW"
    assert manifest.provider == "test_provider"
    assert manifest.symbol == "RELIANCE"
    assert manifest.timeframe == "1D"
    assert manifest.requested_start == "2025-01-01"
    assert manifest.requested_end == "2025-01-05"
    assert manifest.actual_first_date == "2025-01-01"
    assert manifest.actual_last_date == "2025-01-01"
    assert manifest.row_count == 1
    assert manifest.adjustment_status == "RAW_UNADJUSTED"
    assert manifest.calendar_identity == "NSE_EQUITY_DAILY"
    assert manifest.calendar_sha256 == "abc123sha"
    assert len(manifest.raw_sha256) == 64

def test_s41_a03_raw_sha_equals_exact_bytes(tmp_path):
    csv_path = tmp_path / "raw.csv"
    raw_content = b"Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n"
    csv_path.write_bytes(raw_content)
    
    expected_hash = hashlib.sha256(raw_content).hexdigest()
    
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path,
        source_identity="RELIANCE_1D_RAW",
        provider="test_provider",
        symbol="RELIANCE",
        timeframe="1D",
        requested_start="2025-01-01",
        requested_end="2025-01-05",
        adjustment_status="RAW_UNADJUSTED",
        calendar_identity="NSE_EQUITY_DAILY",
        calendar_sha256="abc123sha"
    )
    
    assert manifest.raw_sha256 == expected_hash

def test_s41_a04_one_byte_mutation_fails(tmp_path):
    csv_path = tmp_path / "raw.csv"
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n", encoding="utf-8")
    
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path,
        source_identity="RELIANCE_1D_RAW",
        provider="test_provider",
        symbol="RELIANCE",
        timeframe="1D",
        requested_start="2025-01-01",
        requested_end="2025-01-05",
        adjustment_status="RAW_UNADJUSTED",
        calendar_identity="NSE_EQUITY_DAILY",
        calendar_sha256="abc123sha"
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest.to_dict()))
    
    # Mutate CSV byte
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,103,1000\n", encoding="utf-8")
    
    valid, err = QualificationManager.verify_sidecar(csv_path, manifest_path)
    assert not valid
    assert "hash mismatch" in err.lower()

def test_s41_a10_missing_manifest_rejected(tmp_path):
    csv_path = tmp_path / "raw.csv"
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n", encoding="utf-8")
    manifest_path = tmp_path / "nonexistent.json"
    
    valid, err = QualificationManager.verify_sidecar(csv_path, manifest_path)
    assert not valid

def test_s41_a12_retrieved_at_provenance_independence(tmp_path):
    csv_path = tmp_path / "raw.csv"
    raw_content = b"Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n"
    csv_path.write_bytes(raw_content)
    
    m1 = QualificationManager.generate_manifest(
        csv_path=csv_path, source_identity="X", provider="P", symbol="S", timeframe="1D",
        requested_start="2025-01-01", requested_end="2025-01-05", adjustment_status="RAW_UNADJUSTED",
        calendar_identity="CAL", calendar_sha256="HASH"
    )
    m2 = QualificationManager.generate_manifest(
        csv_path=csv_path, source_identity="X", provider="P", symbol="S", timeframe="1D",
        requested_start="2025-01-01", requested_end="2025-01-05", adjustment_status="RAW_UNADJUSTED",
        calendar_identity="CAL", calendar_sha256="HASH"
    )
    
    # Same raw bytes must produce identical raw_sha256 even if timestamps differ slightly
    assert m1.raw_sha256 == m2.raw_sha256


def test_s41_a06_sidecar_pairing_failure_modes(tmp_path):
    csv_path = tmp_path / "raw.csv"
    manifest_path = tmp_path / "manifest.json"
    
    # Neither exists
    valid, _ = QualificationManager.verify_sidecar(csv_path, manifest_path)
    assert not valid
    
    # CSV exists, manifest missing
    csv_path.write_text("Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n", encoding="utf-8")
    valid, _ = QualificationManager.verify_sidecar(csv_path, manifest_path)
    assert not valid
    
    # Manifest exists, CSV missing
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path, source_identity="X", provider="P", symbol="S", timeframe="1D",
        requested_start="2025-01-01", requested_end="2025-01-05", adjustment_status="RAW_UNADJUSTED",
        calendar_identity="CAL", calendar_sha256="HASH"
    )
    manifest_path.write_text(json.dumps(manifest.to_dict()), encoding="utf-8")
    csv_path.unlink()
    
    valid, _ = QualificationManager.verify_sidecar(csv_path, manifest_path)
    assert not valid

def test_s41_a07_exact_persisted_row_count(tmp_path):
    csv_path = tmp_path / "raw.csv"
    # Exactly 3 data lines + header
    raw_content = b"Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n2025-01-02,100,105,95,103,1100\n2025-01-03,100,105,95,104,1200\n"
    csv_path.write_bytes(raw_content)
    
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path, source_identity="X", provider="P", symbol="S", timeframe="1D",
        requested_start="2025-01-01", requested_end="2025-01-05", adjustment_status="RAW_UNADJUSTED",
        calendar_identity="CAL", calendar_sha256="HASH"
    )
    assert manifest.row_count == 3

def test_s41_a08_p43_handoff_boundary(tmp_path):
    # Verify that a qualified raw CSV successfully passes verification and is ready for P4.3 input preparation
    csv_path = tmp_path / "raw.csv"
    csv_content = b"Date,Open,High,Low,Close,Volume\n2025-01-01,100,105,95,102,1000\n"
    csv_path.write_bytes(csv_content)
    
    manifest = QualificationManager.generate_manifest(
        csv_path=csv_path, source_identity="RELIANCE_1D_RAW", provider="test", symbol="RELIANCE", timeframe="1D",
        requested_start="2025-01-01", requested_end="2025-01-01", adjustment_status="RAW_UNADJUSTED",
        calendar_identity="NSE_EQUITY_DAILY", calendar_sha256="hash123"
    )
    
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest.to_dict()), encoding="utf-8")
    
    valid, err = QualificationManager.verify_sidecar(csv_path, manifest_path)
    assert valid
    assert err == "OK"
    
    # Handoff confirmation: The artifact satisfies the acquisition boundary requirements expected by P4.3
    assert manifest.raw_sha256 is not None
    assert manifest.row_count == 1
