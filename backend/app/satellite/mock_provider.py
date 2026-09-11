import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.satellite.base import SatelliteProvider
from backend.app.domain.models import ImageMetadata, SensorType

class MockSatelliteProvider(SatelliteProvider):
    def __init__(self):
        super().__init__(provider_name="SIH Mock Satellite Provider")
        self._scenes = {
            "SCENE-KOLKATA-2024": ImageMetadata(
                id="SCENE-KOLKATA-2024",
                sensor=SensorType.OPTICAL_SENTINEL2,
                date="2024-05-20",
                spatial_resolution_m=10.0,
                cloud_cover_percent=3.2,
                bbox=[88.214, 22.451, 88.482, 22.689]
            ),
            "SCENE-BHUBANESWAR-2023": ImageMetadata(
                id="SCENE-BHUBANESWAR-2023",
                sensor=SensorType.OPTICAL_LANDSAT,
                date="2023-11-14",
                spatial_resolution_m=30.0,
                cloud_cover_percent=1.1,
                bbox=[85.780, 20.240, 85.880, 20.350]
            ),
            "SCENE-ASSAM-SAR-2024": ImageMetadata(
                id="SCENE-ASSAM-SAR-2024",
                sensor=SensorType.SAR_SENTINEL1,
                date="2024-07-02",
                spatial_resolution_m=10.0,
                cloud_cover_percent=0.0,
                bbox=[93.100, 26.500, 93.300, 26.700]
            ),
            "SCENE-DELHI-AIRPORT-2024": ImageMetadata(
                id="SCENE-DELHI-AIRPORT-2024",
                sensor=SensorType.HIGH_RES,
                date="2024-02-10",
                spatial_resolution_m=0.3,
                cloud_cover_percent=0.5,
                bbox=[77.080, 28.540, 77.120, 28.580]
            )
        }

    def discover_scenes(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        max_cloud: float = 15.0
    ) -> List[ImageMetadata]:
        return [img for img in self._scenes.values() if img.cloud_cover_percent <= max_cloud]

    def fetch_metadata(self, scene_id: str) -> Optional[ImageMetadata]:
        return self._scenes.get(scene_id)

    def get_band_data(self, scene_id: str, band_name: str) -> np.ndarray:
        np.random.seed(abs(hash(scene_id + band_name)) % (2**32 - 1))
        
        # Use consistent array size for all bands to enable coregistration
        arr_size = 512
        
        # Spectral band reflectance simulation based on band type
        if "B8" in band_name or "NIR" in band_name:
            return np.random.uniform(0.35, 0.75, (arr_size, arr_size)).astype(np.float32)
        elif "B4" in band_name or "RED" in band_name:
            return np.random.uniform(0.04, 0.18, (arr_size, arr_size)).astype(np.float32)
        elif "B3" in band_name or "GREEN" in band_name:
            return np.random.uniform(0.08, 0.28, (arr_size, arr_size)).astype(np.float32)
        elif "B11" in band_name or "SWIR" in band_name:
            return np.random.uniform(0.05, 0.30, (arr_size, arr_size)).astype(np.float32)
        elif "VV" in band_name or "VH" in band_name:
            return np.random.uniform(40.0, 280.0, (arr_size, arr_size)).astype(np.float32)
        else:
            return np.random.uniform(0.1, 0.5, (arr_size, arr_size)).astype(np.float32)

    def get_valid_pixel_ratio(self, scene_id: str) -> float:
        """Mock implementation: return high valid pixel ratio for testing."""
        return 0.98

    def get_rgb_preview(self, scene_id: str) -> str:
        """Mock implementation: return a placeholder data URI."""
        # Return a 1x1 transparent PNG as placeholder
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
