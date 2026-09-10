from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, List
from backend.app.domain.models import AnalysisRequest, GroundingMask, ChangeMapResult, SpectralIndices
from backend.app.domain.evidence import EvidenceCollector
from backend.app.satellite.base import SatelliteProvider

class BaseSpecialist(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(
        self,
        request: AnalysisRequest,
        evidence_collector: EvidenceCollector,
        provider: Optional[SatelliteProvider] = None,
        scene_id: str = "",
        comparison_scene_id: Optional[str] = None,
    ) -> Tuple[str, List[GroundingMask], Optional[ChangeMapResult], Optional[SpectralIndices]]:
        """
        Executes the specialist analysis logic using real or mock provider band data.
        Returns tuple: (summary_answer, grounding_masks, change_map, spectral_indices)
        """
        pass
