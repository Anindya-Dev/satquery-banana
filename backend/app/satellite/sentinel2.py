import numpy as np
from typing import List, Optional
from backend.app.satellite.base import SatelliteProvider
from backend.app.domain.models import ImageMetadata, SensorType
from backend.app.core.exceptions import SatelliteDataUnavailableError

class Sentinel2Provider(SatelliteProvider):
    def __init__(self, stac_api_url: str = "https://earth-search.aws.element84.com/v1"):
        super().__init__(provider_name="Sentinel-2 L2A STAC Client")
        self.stac_api_url = stac_api_url

    def discover_scenes(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        max_cloud: float = 15.0
    ) -> List[ImageMetadata]:
        # Production STAC query client wrapper stub
        return [
            ImageMetadata(
                id="S2A_MSIL2A_20240520T050641_N0510_R019_T45QXE",
                sensor=SensorType.OPTICAL_SENTINEL2,
                date=start_date or "2024-05-20",
                spatial_resolution_m=10.0,
                cloud_cover_percent=4.2,
                bbox=bbox
            )
        ]

    def fetch_metadata(self, scene_id: str) -> Optional[ImageMetadata]:
        return ImageMetadata(
            id=scene_id,
            sensor=SensorType.OPTICAL_SENTINEL2,
            date="2024-05-20",
            cloud_cover_percent=4.2
        )

    def get_band_data(self, scene_id: str, band_name: str) -> np.ndarray:
        raise SatelliteDataUnavailableError(
            f"Live Copernicus download for scene '{scene_id}' requires credentials. "
            "Please use MockSatelliteProvider for offline evaluation testing."
        )
