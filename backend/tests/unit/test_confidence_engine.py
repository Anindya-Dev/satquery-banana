import pytest
from backend.app.domain.confidence import ConfidenceScorer
from backend.app.domain.models import CoRegistrationQuality

def test_confidence_valid_pixel_monotonicity():
    conf_low_valid = ConfidenceScorer.calculate(valid_pixel_ratio=0.80, cloud_percent=0.0)
    conf_high_valid = ConfidenceScorer.calculate(valid_pixel_ratio=0.98, cloud_percent=0.0)
    
    assert conf_high_valid.score >= conf_low_valid.score

def test_confidence_cloud_cover_monotonicity():
    conf_clear = ConfidenceScorer.calculate(valid_pixel_ratio=1.0, cloud_percent=2.0)
    conf_cloudy = ConfidenceScorer.calculate(valid_pixel_ratio=1.0, cloud_percent=14.0)
    
    assert conf_cloudy.score <= conf_clear.score

def test_confidence_coregistration_monotonicity():
    coreg_good = CoRegistrationQuality(total_shift_px=1.0, is_aligned=True, correlation_score=0.98)
    coreg_degraded = CoRegistrationQuality(total_shift_px=5.5, is_aligned=False, applied_warp=True, correlation_score=0.70)
    
    conf_good = ConfidenceScorer.calculate(valid_pixel_ratio=1.0, cloud_percent=0.0, coregistration=coreg_good)
    conf_degraded = ConfidenceScorer.calculate(valid_pixel_ratio=1.0, cloud_percent=0.0, coregistration=coreg_degraded)
    
    assert conf_degraded.score <= conf_good.score

def test_confidence_spectral_sanity_monotonicity():
    conf_sane = ConfidenceScorer.calculate(valid_pixel_ratio=1.0, cloud_percent=0.0, spectral_sane=True)
    conf_insane = ConfidenceScorer.calculate(valid_pixel_ratio=1.0, cloud_percent=0.0, spectral_sane=False)
    
    assert conf_insane.score < conf_sane.score
