from typing import List, Tuple, Optional, Dict, Any
from backend.app.domain.models import ImageMetadata, CoRegistrationQuality
from backend.app.core.config import settings

class EvidenceSufficiencyGate:
    @staticmethod
    def evaluate_sufficiency(
        images: List[ImageMetadata] = [],
        valid_pixel_ratio: float = 1.0,
        coregistration: Optional[CoRegistrationQuality] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Determines whether gathered evidence is sufficient to answer query BEFORE invoking VLM.
        Returns (is_sufficient, refusal_reason).
        """
        if valid_pixel_ratio < settings.MIN_VALID_PIXEL_RATIO:
            return False, (
                f"Refusal Triggered: Insufficient valid pixels ({valid_pixel_ratio*100:.1f}%). "
                f"Minimum required valid pixel ratio is {settings.MIN_VALID_PIXEL_RATIO*100:.1f}%."
            )

        for img in images:
            if img.cloud_cover_percent > settings.MAX_ALLOWED_CLOUD_PERCENT:
                return False, (
                    f"Refusal Triggered: Cloud cover obstruction ({img.cloud_cover_percent}%) "
                    f"exceeds maximum quality threshold of {settings.MAX_ALLOWED_CLOUD_PERCENT}%."
                )

        if coregistration:
            if coregistration.total_shift_px > settings.MAX_DEGRADED_COREGISTRATION_SHIFT_PX:
                return False, (
                    f"Refusal Triggered: Severe spatial mis-alignment between bi-temporal scenes ({coregistration.total_shift_px:.2f}px shift > {settings.MAX_DEGRADED_COREGISTRATION_SHIFT_PX:.1f}px). "
                    "Unusable co-registration quality. Cannot compute pixel-wise change detection."
                )

        return True, None
