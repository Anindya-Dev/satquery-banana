from typing import List, Optional, Tuple

import cv2
import numpy as np

from backend.app.core.exceptions import SatelliteDataUnavailableError
from backend.app.domain.evidence import EvidenceCollector
from backend.app.domain.models import AnalysisRequest, ChangeMapResult, GroundingMask, SpectralIndices
from backend.app.geospatial.bbox import SpatialBBoxOps
from backend.app.geospatial.raster_ops import RasterOps
from backend.app.satellite.base import SatelliteProvider
from backend.app.specialists.base import BaseSpecialist


class GroundingSpecialist(BaseSpecialist):
    """Segments supported land-cover targets from measured Sentinel-2 spectral indices."""

    def __init__(self):
        super().__init__(name="Spectral Segmentation Specialist")

    def execute(
        self,
        request: AnalysisRequest,
        evidence_collector: EvidenceCollector,
        provider: Optional[SatelliteProvider] = None,
        scene_id: str = "",
    ) -> Tuple[str, List[GroundingMask], Optional[ChangeMapResult], Optional[SpectralIndices]]:
        if provider is None or not request.bbox:
            raise SatelliteDataUnavailableError("Live segmentation requires a selected scene and an analysis area.")

        query = request.query.lower()
        if any(word in query for word in ("water", "river", "lake", "flood")):
            index = RasterOps.calculate_ndwi(provider.get_band_data(scene_id, "B3"), provider.get_band_data(scene_id, "B8"))
            binary = (index > 0.05).astype(np.uint8)
            label, index_name = "Open water", "NDWI"
        elif any(word in query for word in ("vegetation", "forest", "crop", "canopy")):
            index = RasterOps.calculate_ndvi(provider.get_band_data(scene_id, "B8"), provider.get_band_data(scene_id, "B4"))
            binary = (index > 0.30).astype(np.uint8)
            label, index_name = "Vegetation", "NDVI"
        else:
            raise SatelliteDataUnavailableError(
                "Live segmentation supports water and vegetation from Sentinel-2 spectral masks. "
                "Arbitrary objects require high-resolution imagery and a dedicated model."
            )

        count, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        if count <= 1:
            raise SatelliteDataUnavailableError(f"No {label.lower()} component met the live {index_name} threshold.")
        component = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        x, y, width, height, pixels = stats[component]
        rows, cols = binary.shape
        xmin, ymin, xmax, ymax = request.bbox
        component_bbox = [
            xmin + x / cols * (xmax - xmin),
            ymax - (y + height) / rows * (ymax - ymin),
            xmin + (x + width) / cols * (xmax - xmin),
            ymax - y / rows * (ymax - ymin),
        ]
        area_sq_m = SpatialBBoxOps.calculate_area_sq_km(request.bbox) * 1_000_000 * pixels / binary.size
        mask = GroundingMask(
            id="MASK-SPECTRAL-01",
            label=f"{label} spectral mask",
            confidence=float(round(min(0.99, 0.5 + pixels / binary.size), 2)),
            bbox=component_bbox,
            polygon_geojson=SpatialBBoxOps.bbox_to_geojson(component_bbox),
            area_sq_m=float(round(area_sq_m, 2)),
        )
        evidence_collector.add(
            evidence_type="SpectralSegmentation",
            layer=f"Sentinel-2 {index_name} threshold mask",
            description=f"Largest connected {label.lower()} component extracted from live raster pixels.",
            metric_name="Segmented_Area",
            metric_value=float(round(area_sq_m, 2)),
            unit="sq_m",
            bbox=component_bbox,
        )
        
        # Compute spectral indices for the scene
        index_stats = RasterOps.get_index_stats(index)
        
        if label == "Open water":
            spectral_indices = SpectralIndices(
                ndwi_mean=index_stats['mean'],
                mndwi_mean=index_stats['mean']
            )
        else:
            spectral_indices = SpectralIndices(
                ndvi_mean=index_stats['mean']
            )
        
        return f"Segmented the largest {label.lower()} component covering {area_sq_m:.0f} sq m from a live {index_name} mask.", [mask], None, spectral_indices
