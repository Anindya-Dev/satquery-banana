import numpy as np
from typing import Tuple, List, Optional
from backend.app.specialists.base import BaseSpecialist
from backend.app.domain.models import AnalysisRequest, GroundingMask, ChangeMapResult, SpectralIndices
from backend.app.domain.evidence import EvidenceCollector
from backend.app.geospatial.raster_ops import RasterOps
from backend.app.geospatial.bbox import SpatialBBoxOps
from backend.app.satellite.base import SatelliteProvider

class ChangeDetectionSpecialist(BaseSpecialist):
    def __init__(self):
        super().__init__(name="Bi-Temporal Change Detection Specialist")

    def execute(
        self,
        request: AnalysisRequest,
        evidence_collector: EvidenceCollector,
        provider: Optional[SatelliteProvider] = None,
        scene_id: str = "",
        comparison_scene_id: Optional[str] = None,
    ) -> Tuple[str, List[GroundingMask], Optional[ChangeMapResult], Optional[SpectralIndices]]:
        if provider is None or not comparison_scene_id:
            raise ValueError("Change detection requires two real selected satellite scenes.")
        prov = provider
        
        # Retrieve T1 and T2 band data from SatelliteProvider abstraction
        t1_green = prov.get_band_data(comparison_scene_id, "B3")
        t1_nir = prov.get_band_data(comparison_scene_id, "B8")
        t2_green = prov.get_band_data(scene_id, "B3")
        t2_nir = prov.get_band_data(scene_id, "B8")

        t1_ndwi = RasterOps.calculate_ndwi(t1_green, t1_nir)
        t2_ndwi = RasterOps.calculate_ndwi(t2_green, t2_nir)
        
        # Also compute NDVI for both periods
        t1_red = prov.get_band_data(comparison_scene_id, "B4")
        t2_red = prov.get_band_data(scene_id, "B4")
        t1_ndvi = RasterOps.calculate_ndvi(t1_nir, t1_red)
        t2_ndvi = RasterOps.calculate_ndvi(t2_nir, t2_red)

        diff, change_mask, pct_changed = RasterOps.compute_bitemporal_diff(t1_ndwi, t2_ndwi, threshold=0.25)
        if not request.bbox:
            raise ValueError("Change detection requires a resolved analysis bounding box.")
        changed_sq_km = float(np.round((pct_changed / 100.0) * SpatialBBoxOps.calculate_area_sq_km(request.bbox), 2))

        # Compute spectral index statistics
        t1_ndwi_stats = RasterOps.get_index_stats(t1_ndwi)
        t2_ndwi_stats = RasterOps.get_index_stats(t2_ndwi)
        t1_ndvi_stats = RasterOps.get_index_stats(t1_ndvi)
        t2_ndvi_stats = RasterOps.get_index_stats(t2_ndvi)

        evidence_collector.add(
            evidence_type="BitemporalDiff",
            layer=f"{prov.provider_name} T1 vs T2",
            description=f"Pixel-wise NDWI change exceeded the configured threshold across {pct_changed}% of the analysis area.",
            metric_name="Changed_Area",
            metric_value=changed_sq_km,
            unit="sq_km"
        )

        evidence_collector.add(
            evidence_type="SpectralShift",
            layer="NDWI Shift Matrix",
            description=f"Mean NDWI changed from {t1_ndwi_stats['mean']:.2f} (T1 pre-event) to {t2_ndwi_stats['mean']:.2f} (T2 post-event).",
            metric_name="NDWI_Delta",
            metric_value=float(np.round(t2_ndwi_stats['mean'] - t1_ndwi_stats['mean'], 2)),
            unit="index delta"
        )

        evidence_collector.add(
            evidence_type="SpectralShift",
            layer="NDVI Shift Matrix",
            description=f"Mean NDVI changed from {t1_ndvi_stats['mean']:.2f} (T1 pre-event) to {t2_ndvi_stats['mean']:.2f} (T2 post-event).",
            metric_name="NDVI_Delta",
            metric_value=float(np.round(t2_ndvi_stats['mean'] - t1_ndvi_stats['mean'], 2)),
            unit="index delta"
        )

        change_result = ChangeMapResult(
            changed_area_sq_km=changed_sq_km,
            percent_change=pct_changed,
            change_type="Observed NDWI change",
            confidence=0.0,
            class_breakdown={
                "Thresholded NDWI change": changed_sq_km,
            },
            change_polygons_count=0
        )

        spectral_indices = SpectralIndices(
            ndwi_mean=t2_ndwi_stats['mean'],
            ndvi_mean=t2_ndvi_stats['mean'],
            mndwi_mean=t2_ndwi_stats['mean']
        )

        answer = (
            f"Bi-temporal analysis measured {changed_sq_km} sq km of thresholded NDWI change "
            f"({pct_changed}% of the requested area) between the selected acquisitions. "
            f"Mean NDWI shifted from {t1_ndwi_stats['mean']:.2f} to {t2_ndwi_stats['mean']:.2f}, "
            f"and mean NDVI shifted from {t1_ndvi_stats['mean']:.2f} to {t2_ndvi_stats['mean']:.2f}."
        )

        return answer, [], change_result, spectral_indices
