from typing import Optional

import numpy as np

from backend.app.core.config import settings
from backend.app.core.exceptions import SatelliteDataUnavailableError
from backend.app.domain.models import SensorType
from backend.app.satellite.sentinel2 import Sentinel2Provider


class Sentinel1RTCProvider(Sentinel2Provider):
    """Reads precomputed Sentinel-1 radiometrically terrain-corrected VV/VH assets."""

    def __init__(self, stac_api_url: Optional[str] = None):
        if not settings.PLANETARY_COMPUTER_SUBSCRIPTION_KEY:
            raise SatelliteDataUnavailableError(
                "Sentinel-1 RTC requires PLANETARY_COMPUTER_SUBSCRIPTION_KEY in the Render environment."
            )
        super().__init__(
            stac_api_url=stac_api_url,
            collection="sentinel-1-rtc",
            provider_name="Microsoft Planetary Computer Sentinel-1 RTC",
        )

    def get_valid_pixel_ratio(self, scene_id: str) -> float:
        band = self.get_band_data(scene_id, "vv")
        return float(np.mean(np.isfinite(band) & (band > 0))) if band.size else 0.0
