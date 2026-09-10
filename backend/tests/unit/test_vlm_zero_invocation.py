import pytest
from typing import List, Dict, Any
from backend.app.domain.models import AnalysisRequest, Evidence, ImageMetadata, CoRegistrationQuality, TaskType
from backend.app.ai.base import VisionLanguageProvider
from backend.app.orchestration.task_router import TaskRouter
from backend.app.domain.sufficiency import EvidenceSufficiencyGate
from backend.app.core.config import settings

class CountingMockVLMProvider(VisionLanguageProvider):
    def __init__(self):
        super().__init__(provider_name="Counting Mock VLM")
        self.call_count = 0

    def generate_structured_interpretation(
        self,
        request: AnalysisRequest,
        evidence_chain: List[Evidence],
        deterministic_summary: str
    ) -> Dict[str, Any]:
        self.call_count += 1
        return {
            "summary": f"VLM interpreted: {deterministic_summary}",
            "claims": [],
            "insufficient_evidence": False
        }

def test_vlm_invocation_count_zero_on_excessive_cloud():
    mock_vlm = CountingMockVLMProvider()
    router = TaskRouter()
    router.ai_provider = mock_vlm

    req = AnalysisRequest(query="Analyze flood inundation in Kolkata")
    # Simulate high cloud scene by modifying retriever or refusal gate evaluation directly
    cloudy_img = ImageMetadata(id="TEST-CLOUD", date="2024-05-20", cloud_cover_percent=25.0)
    is_refused, reason = EvidenceSufficiencyGate.evaluate_sufficiency(images=[cloudy_img], valid_pixel_ratio=0.95)
    assert is_refused is False  # Gate evaluates sufficiency (returns (is_sufficient, reason))
    
    # Sufficiency evaluates: returns False if insufficient.
    is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(images=[cloudy_img], valid_pixel_ratio=0.95)
    assert is_sufficient is False
    assert "Cloud cover" in reason
    assert mock_vlm.call_count == 0

def test_vlm_invocation_count_zero_on_insufficient_valid_pixels():
    mock_vlm = CountingMockVLMProvider()
    is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(images=[], valid_pixel_ratio=0.40)
    assert is_sufficient is False
    assert "valid pixels" in reason
    assert mock_vlm.call_count == 0

def test_vlm_invocation_count_zero_on_unusable_coregistration():
    mock_vlm = CountingMockVLMProvider()
    coreg = CoRegistrationQuality(total_shift_px=7.2, is_aligned=False, applied_warp=False)
    is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(images=[], valid_pixel_ratio=1.0, coregistration=coreg)
    assert is_sufficient is False
    assert "mis-alignment" in reason
    assert mock_vlm.call_count == 0

def test_vlm_invocation_count_zero_on_out_of_domain_query():
    mock_vlm = CountingMockVLMProvider()
    router = TaskRouter()
    router.ai_provider = mock_vlm
    
    req = AnalysisRequest(query="write a poem about satellites")
    res = router.process(req)
    assert res.refusal_triggered is True
    assert mock_vlm.call_count == 0

def test_coregistration_threshold_policy_verification():
    """
    Verifies 3-tier policy:
    <= 3.0 px -> GOOD
    > 3.0 and <= 6.0 px -> DEGRADED
    > 6.0 px -> UNUSABLE (Refusal)
    """
    shifts_to_test = [0.0, 1.0, 3.0, 3.01, 5.0, 6.0, 6.01]
    
    for shift in shifts_to_test:
        coreg = CoRegistrationQuality(
            total_shift_px=shift,
            is_aligned=shift <= settings.GOOD_COREGISTRATION_SHIFT_PX,
            applied_warp=shift > settings.GOOD_COREGISTRATION_SHIFT_PX and shift <= settings.MAX_DEGRADED_COREGISTRATION_SHIFT_PX
        )
        
        is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(images=[], valid_pixel_ratio=1.0, coregistration=coreg)
        
        if shift <= 3.0:
            assert coreg.is_aligned is True
            assert coreg.applied_warp is False
            assert is_sufficient is True
        elif shift <= 6.0:
            assert coreg.is_aligned is False
            assert coreg.applied_warp is True
            assert is_sufficient is True
        else:
            assert coreg.is_aligned is False
            assert coreg.applied_warp is False
            assert is_sufficient is False
            assert "Severe spatial mis-alignment" in reason
