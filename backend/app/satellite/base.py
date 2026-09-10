from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from backend.app.domain.models import ImageMetadata, SensorType

class SatelliteProvider(ABC):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    def discover_scenes(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        max_cloud: float = 15.0
    ) -> List[ImageMetadata]:
        """Discovers available satellite scenes intersecting bbox and temporal range."""
        pass

    @abstractmethod
    def fetch_metadata(self, scene_id: str) -> Optional[ImageMetadata]:
        """Fetches metadata object for a given scene ID."""
        pass

    @abstractmethod
    def get_band_data(self, scene_id: str, band_name: str) -> np.ndarray:
        """Retrieves 2D NumPy array buffer for requested band."""
        pass
