import numpy as np
import cv2
from backend.app.geospatial.coregistration import CoRegistrationEngine
from backend.app.domain.confidence import ConfidenceScorer
from backend.app.domain.models import CoRegistrationQuality

def test_aligned_images_shift_zero():
    np.random.seed(42)
    img1 = np.random.uniform(0, 255, (256, 256)).astype(np.uint8)
    img2 = img1.copy()
    
    quality = CoRegistrationEngine.evaluate_alignment(img1, img2)
    assert quality.total_shift_px < 0.5
    assert quality.is_aligned is True

def test_translated_images_shift_detection():
    img1 = np.zeros((256, 256), dtype=np.uint8)
    cv2.rectangle(img1, (50, 50), (150, 150), 255, -1)

    # Shift image by (3px horizontal, 0px vertical)
    M = np.float32([[1, 0, 3], [0, 1, 0]])
    img2 = cv2.warpAffine(img1, M, (256, 256))

    quality = CoRegistrationEngine.evaluate_alignment(img1, img2)
    assert abs(quality.shift_x_px - 3.0) < 1.0

def test_coregistration_confidence_penalty_propagation():
    """Verify registration shift degrades confidence appropriately."""
    good_coreg = CoRegistrationQuality(total_shift_px=1.0, is_aligned=True, correlation_score=0.98)
    degraded_coreg = CoRegistrationQuality(total_shift_px=5.0, is_aligned=False, applied_warp=True, correlation_score=0.75)

    conf_good = ConfidenceScorer.calculate(valid_pixel_ratio=1.0, cloud_percent=0.0, coregistration=good_coreg)
    conf_degraded = ConfidenceScorer.calculate(valid_pixel_ratio=1.0, cloud_percent=0.0, coregistration=degraded_coreg)

    # Confidence score MUST be lower for degraded co-registration
    assert conf_degraded.score < conf_good.score
    assert conf_degraded.factors.coregistration_penalty > conf_good.factors.coregistration_penalty
