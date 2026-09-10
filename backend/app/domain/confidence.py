from typing import Optional
from backend.app.domain.models import Confidence, ConfidenceFactors, CoRegistrationQuality

class ConfidenceScorer:
    @staticmethod
    def calculate(
        valid_pixel_ratio: float = 1.0,
        cloud_percent: float = 0.0,
        coregistration: Optional[CoRegistrationQuality] = None,
        spectral_sane: bool = True
    ) -> Confidence:
        # Penalties calculation
        cloud_penalty = min(cloud_percent / 100.0, 1.0) * 0.4
        
        coreg_penalty = 0.0
        if coregistration:
            if not coregistration.is_aligned:
                coreg_penalty = min(coregistration.total_shift_px / 10.0, 0.5)
            else:
                coreg_penalty = (1.0 - coregistration.correlation_score) * 0.2
        
        spectral_sanity_score = 1.0 if spectral_sane else 0.5

        # Raw formula: Base valid pixel ratio - cloud penalty - coregistration penalty * spectral sanity
        base_score = valid_pixel_ratio * 0.95
        raw_score = (base_score - cloud_penalty - coreg_penalty) * spectral_sanity_score
        
        # Clamp score between 0.0 and 1.0
        score = max(0.05, min(0.99, round(raw_score, 4)))

        if score >= 0.85:
            rating = "HIGH"
        elif score >= 0.65:
            rating = "MEDIUM"
        else:
            rating = "LOW"

        factors = ConfidenceFactors(
            valid_pixel_ratio=round(valid_pixel_ratio, 4),
            cloud_penalty=round(cloud_penalty, 4),
            coregistration_penalty=round(coreg_penalty, 4),
            spectral_sanity_score=round(spectral_sanity_score, 4)
        )

        return Confidence(score=score, rating=rating, factors=factors)
