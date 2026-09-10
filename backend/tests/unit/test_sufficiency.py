from backend.app.domain.sufficiency import EvidenceSufficiencyGate
from backend.app.domain.models import ImageMetadata, CoRegistrationQuality

def test_sufficiency_gate_valid_pass():
    img = ImageMetadata(id="S2-TEST", date="2024-05-20", cloud_cover_percent=4.2)
    is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(
        images=[img],
        valid_pixel_ratio=0.95
    )
    assert is_sufficient is True
    assert reason is None

def test_sufficiency_gate_refuse_low_valid_pixels():
    img = ImageMetadata(id="S2-TEST", date="2024-05-20", cloud_cover_percent=4.2)
    is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(
        images=[img],
        valid_pixel_ratio=0.50 # below 0.75 threshold
    )
    assert is_sufficient is False
    assert "Insufficient valid pixels" in reason

def test_sufficiency_gate_refuse_high_cloud():
    img = ImageMetadata(id="S2-TEST", date="2024-05-20", cloud_cover_percent=28.0) # > 15% threshold
    is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(
        images=[img],
        valid_pixel_ratio=0.95
    )
    assert is_sufficient is False
    assert "Cloud cover obstruction" in reason
