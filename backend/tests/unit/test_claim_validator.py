from backend.app.domain.claim_validator import ClaimValidator
from backend.app.domain.evidence import EvidenceCollector
from backend.app.domain.models import Evidence

def test_claim_validator_attaches_citation():
    collector = EvidenceCollector()
    ev = collector.add(
        evidence_type="BandMath",
        layer="Sentinel-2 B8/B4",
        description="NDVI calculated",
        metric_name="NDVI_mean",
        metric_value=0.42,
        unit="index"
    )
    raw_claim = "Vegetation vitality is high."
    grounded = ClaimValidator.validate_and_ground(raw_claim, collector.get_all())
    assert ev.evidence_id in grounded

def test_claim_validator_blocks_causal_leap():
    collector = EvidenceCollector()
    ev = collector.add(
        evidence_type="BandMath",
        layer="Sentinel-2 B3/B8",
        description="NDWI calculated",
        metric_name="NDWI_mean",
        metric_value=0.18,
        unit="index"
    )
    raw_claim = "Industrial pollution caused water turbidity to change."
    grounded = ClaimValidator.validate_and_ground(raw_claim, collector.get_all())
    assert "pollution caused" not in grounded.lower()
    assert "correlated with observed spectral shift" in grounded

def test_claim_validator_empty_evidence_list():
    raw_claim = "High vegetation density observed."
    grounded = ClaimValidator.validate_and_ground(raw_claim, [])
    assert "[GROUNDING WARNING: Zero deterministic evidence gathered" in grounded

def test_claim_validator_missing_evidence_id():
    ev = Evidence(
        evidence_id="",
        evidence_type="BandMath",
        layer="B8",
        description="Test",
        metric_name="Test",
        metric_value=1.0
    )
    grounded = ClaimValidator.validate_and_ground("Some observation.", [ev])
    assert "[GROUNDING REFUSAL: No valid evidence ID present]" in grounded
