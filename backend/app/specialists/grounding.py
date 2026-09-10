from typing import Tuple, List, Optional
from backend.app.specialists.base import BaseSpecialist
from backend.app.domain.models import AnalysisRequest, GroundingMask, ChangeMapResult, SpectralIndices
from backend.app.domain.evidence import EvidenceCollector
from backend.app.geospatial.bbox import SpatialBBoxOps
from backend.app.satellite.base import SatelliteProvider
from backend.app.core.exceptions import SatelliteDataUnavailableError

class GroundingSpecialist(BaseSpecialist):
    def __init__(self):
        super().__init__(name="Visual Grounding & Segmentation Specialist")

    def execute(
        self,
        request: AnalysisRequest,
        evidence_collector: EvidenceCollector,
        provider: Optional[SatelliteProvider] = None,
        scene_id: str = "SCENE-KOLKATA-2024"
    ) -> Tuple[str, List[GroundingMask], Optional[ChangeMapResult], Optional[SpectralIndices]]:
        raise SatelliteDataUnavailableError(
            "Generic object segmentation is disabled in live mode. Sentinel-2 10 m imagery cannot support the demo's "
            "aircraft/runway claims without a real segmentation model and appropriate high-resolution imagery."
        )
        # Define deterministic spatial bounding boxes matching query intent
        query_lower = request.query.lower()
        
        masks = []
        if "aircraft" in query_lower or "runway" in query_lower or "airport" in query_lower:
            bbox_coords = [88.441, 22.648, 88.455, 22.660]
            geojson = SpatialBBoxOps.bbox_to_geojson(bbox_coords)
            area = SpatialBBoxOps.calculate_area_sq_km(bbox_coords) * 1e6 # in sq m
            masks.append(GroundingMask(
                id="MASK-AIRPORT-01",
                label="Commercial Aircraft & Runway Complex",
                confidence=0.96,
                bbox=bbox_coords,
                polygon_geojson=geojson,
                area_sq_m=area
            ))
            evidence_collector.add(
                evidence_type="SAMGrounding",
                layer="Segment Anything Model (SAM-Geo)",
                description=f"Zero-shot visual grounding isolated target area of {area:.0f} m².",
                metric_name="Grounded_Area",
                metric_value=area,
                unit="sq_m",
                bbox=bbox_coords
            )
            answer = f"Segmented 1 primary airport infrastructure zone spanning {area:.0f} m² with 96% visual grounding confidence."
        else:
            bbox_coords = [88.350, 22.560, 88.375, 22.585]
            geojson = SpatialBBoxOps.bbox_to_geojson(bbox_coords)
            area = SpatialBBoxOps.calculate_area_sq_km(bbox_coords) * 1e6
            masks.append(GroundingMask(
                id="MASK-TARGET-01",
                label="Identified Ground Feature",
                confidence=0.94,
                bbox=bbox_coords,
                polygon_geojson=geojson,
                area_sq_m=area
            ))
            evidence_collector.add(
                evidence_type="SAMGrounding",
                layer="Segment Anything Model (SAM-Geo)",
                description=f"Visual grounding zero-shot polygon bounded area of {area:.0f} m².",
                metric_name="Grounded_Area",
                metric_value=area,
                unit="sq_m",
                bbox=bbox_coords
            )
            answer = f"Successfully grounded object boundary for '{request.query}' covering {area:.0f} m²."

        return answer, masks, None, None
