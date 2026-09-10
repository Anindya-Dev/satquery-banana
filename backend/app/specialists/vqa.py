import numpy as np
from typing import Tuple, List, Optional
from backend.app.specialists.base import BaseSpecialist
from backend.app.domain.models import AnalysisRequest, GroundingMask, ChangeMapResult, SpectralIndices
from backend.app.domain.evidence import EvidenceCollector
from backend.app.geospatial.raster_ops import RasterOps
from backend.app.satellite.base import SatelliteProvider
from backend.app.satellite.mock_provider import MockSatelliteProvider

class VQASpecialist(BaseSpecialist):
    def __init__(self):
        super().__init__(name="Visual Question Answering Specialist")

    def execute(
        self,
        request: AnalysisRequest,
        evidence_collector: EvidenceCollector,
        provider: Optional[SatelliteProvider] = None,
        scene_id: str = "SCENE-KOLKATA-2024"
    ) -> Tuple[str, List[GroundingMask], Optional[ChangeMapResult], Optional[SpectralIndices]]:
        prov = provider or MockSatelliteProvider()
        
        # Retrieve scene band data through SatelliteProvider abstraction
        nir = prov.get_band_data(scene_id, "B8")
        red = prov.get_band_data(scene_id, "B4")
        green = prov.get_band_data(scene_id, "B3")
        swir = prov.get_band_data(scene_id, "B11")

        ndvi_arr = RasterOps.calculate_ndvi(nir, red)
        ndwi_arr = RasterOps.calculate_ndwi(green, nir)
        ndbi_arr = RasterOps.calculate_ndbi(swir, nir)

        ndvi_stats = RasterOps.get_index_stats(ndvi_arr)
        ndwi_stats = RasterOps.get_index_stats(ndwi_arr)
        ndbi_stats = RasterOps.get_index_stats(ndbi_arr)

        # Collect evidence
        evidence_collector.add(
            evidence_type="BandMath",
            layer=f"{prov.provider_name} [{scene_id}] B8 (NIR) / B4 (Red)",
            description=f"Mean NDVI computed across tile via {prov.provider_name}.",
            metric_name="NDVI_mean",
            metric_value=ndvi_stats["mean"],
            unit="index [-1..1]"
        )

        evidence_collector.add(
            evidence_type="BandMath",
            layer=f"{prov.provider_name} [{scene_id}] B3 (Green) / B8 (NIR)",
            description=f"Mean NDWI computed via {prov.provider_name}.",
            metric_name="NDWI_mean",
            metric_value=ndwi_stats["mean"],
            unit="index [-1..1]"
        )

        spectral_indices = SpectralIndices(
            ndvi_mean=ndvi_stats["mean"],
            ndvi_max=ndvi_stats["max"],
            ndwi_mean=ndwi_stats["mean"],
            ndbi_mean=ndbi_stats["mean"]
        )

        answer = (
            f"Sentinel-2 Level-2A measurements for the requested area produced Mean NDVI {ndvi_stats['mean']:.2f}, "
            f"Mean NDWI {ndwi_stats['mean']:.2f}, and Mean NDBI {ndbi_stats['mean']:.2f}. "
            "These are spectral observations, not a causal assessment."
        )

        return answer, [], None, spectral_indices
