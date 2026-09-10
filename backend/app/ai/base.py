from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.app.domain.models import AnalysisRequest, Evidence

class VisionLanguageProvider(ABC):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    def generate_structured_interpretation(
        self,
        request: AnalysisRequest,
        evidence_chain: List[Evidence],
        deterministic_summary: str
    ) -> Dict[str, Any]:
        """
        Generates structured claims bound to evidence_ids.
        Generative models are NEVER permitted to alter numerical facts or invention.
        """
        pass
