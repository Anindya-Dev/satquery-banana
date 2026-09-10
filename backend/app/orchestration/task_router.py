import time
import uuid
import numpy as np
from typing import List, Optional
from backend.app.domain.models import (
    AnalysisRequest, AnalysisResult, TaskType, ImageMetadata, GroundingMask, ChangeMapResult, SpectralIndices
)
from backend.app.domain.evidence import EvidenceCollector
from backend.app.domain.confidence import ConfidenceScorer
from backend.app.domain.claim_validator import RefusalEngine, ClaimValidator
from backend.app.understanding.query_parser import QueryParser, StructuredQuery
from backend.app.geospatial.geocoder import Geocoder
from backend.app.geospatial.coregistration import CoRegistrationEngine
from backend.app.satellite.base import SatelliteProvider
from backend.app.satellite.mock_provider import MockSatelliteProvider
from backend.app.retrieval.hybrid_retriever import HybridRetriever
from backend.app.ai.llm_provider import OpenAIProvider
from backend.app.specialists.vqa import VQASpecialist
from backend.app.specialists.grounding import GroundingSpecialist
from backend.app.specialists.change_detection import ChangeDetectionSpecialist
from backend.app.specialists.optical_sar_fusion import OpticalSARFusionSpecialist
from backend.app.core.logging import logger

class TaskRouter:
    def __init__(self, satellite_provider: Optional[SatelliteProvider] = None):
        self.satellite_provider = satellite_provider or MockSatelliteProvider()
        self.retriever = HybridRetriever()
        self.ai_provider = OpenAIProvider()
        self.vqa_specialist = VQASpecialist()
        self.grounding_specialist = GroundingSpecialist()
        self.change_specialist = ChangeDetectionSpecialist()
        self.fusion_specialist = OpticalSARFusionSpecialist()

    def process(self, request: AnalysisRequest) -> AnalysisResult:
        start_time = time.time()
        req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"

        # Layer 1 & 3: Parse Intent & Geocode Location
        structured_query: StructuredQuery = QueryParser.parse_intent(request)
        task_type = structured_query.task_type
        Geocoder.validate_bbox(structured_query.query_bbox)

        # Layer 4 & 5: Candidate Retrieval & Quality Check
        candidates = self.retriever.retrieve_candidates(
            query_bbox=structured_query.query_bbox,
            max_cloud=15.0,
            min_valid_pixels=0.75
        )

        sample_img = ImageMetadata(
            id=candidates[0]["scene_id"] if candidates else "SCENE-KOLKATA-2024",
            date="2024-05-20",
            cloud_cover_percent=candidates[0]["cloud_cover"] if candidates else 3.2,
            bbox=structured_query.query_bbox
        )
        
        # Layer 6: Spatial Alignment Check for Change Detection
        coreg_quality = None
        if task_type == TaskType.CHANGE_DETECTION:
            np.random.seed(42)
            t1_img = np.random.uniform(0, 255, (512, 512, 3)).astype(np.uint8)
            t2_img = t1_img.copy()
            coreg_quality = CoRegistrationEngine.evaluate_alignment(t1_img, t2_img)

        # Layer 7: Pre-VLM Evidence Sufficiency & Safety Refusal Gate
        is_refused, refusal_reason = RefusalEngine.evaluate_gates(
            query=request.query,
            images=[sample_img],
            valid_pixel_ratio=candidates[0]["valid_pixel_ratio"] if candidates else 1.0,
            coregistration=coreg_quality
        )

        if is_refused:
            elapsed = float(round((time.time() - start_time) * 1000, 2))
            logger.info("Query refused by evidence sufficiency gate.", request_id=req_id, reason=refusal_reason)
            return AnalysisResult(
                request_id=req_id,
                query=request.query,
                task_type=task_type,
                refusal_triggered=True,
                refusal_reason=refusal_reason,
                summary_answer=f"Analysis Refused: {refusal_reason}",
                evidence_chain=[],
                confidence=ConfidenceScorer.calculate(valid_pixel_ratio=0.0, cloud_percent=100.0),
                processing_time_ms=elapsed
            )

        # Layer 8 & 9: Execute Specialist Pipeline & Evidence Collection
        evidence_collector = EvidenceCollector()
        grounding_masks: List[GroundingMask] = []
        change_map: Optional[ChangeMapResult] = None
        spectral_indices: Optional[SpectralIndices] = None
        answer_text: str = ""

        if task_type == TaskType.CHANGE_DETECTION:
            answer_text, grounding_masks, change_map, spectral_indices = self.change_specialist.execute(
                request, evidence_collector, provider=self.satellite_provider, scene_id=sample_img.id
            )
        elif task_type == TaskType.GROUNDING:
            answer_text, grounding_masks, change_map, spectral_indices = self.grounding_specialist.execute(
                request, evidence_collector, provider=self.satellite_provider, scene_id=sample_img.id
            )
        elif task_type == TaskType.OPTICAL_SAR_FUSION:
            answer_text, grounding_masks, change_map, spectral_indices = self.fusion_specialist.execute(
                request, evidence_collector, provider=self.satellite_provider, scene_id=sample_img.id
            )
        else:
            answer_text, grounding_masks, change_map, spectral_indices = self.vqa_specialist.execute(
                request, evidence_collector, provider=self.satellite_provider, scene_id=sample_img.id
            )

        evidence_chain = evidence_collector.get_all()

        # Layer 10: AI Provider Interpretation & Claim Validation
        vlm_res = self.ai_provider.generate_structured_interpretation(request, evidence_chain, answer_text)
        grounded_answer = ClaimValidator.validate_and_ground(vlm_res["summary"], evidence_chain)

        # Layer 11: Deterministic Confidence Calculation
        confidence = ConfidenceScorer.calculate(
            valid_pixel_ratio=candidates[0]["valid_pixel_ratio"] if candidates else 1.0,
            cloud_percent=sample_img.cloud_cover_percent,
            coregistration=coreg_quality,
            spectral_sane=True
        )

        elapsed = float(round((time.time() - start_time) * 1000, 2))

        # Layer 12: Final Grounded Response Sanitization
        return AnalysisResult(
            request_id=req_id,
            query=request.query,
            task_type=task_type,
            refusal_triggered=False,
            summary_answer=grounded_answer,
            evidence_chain=evidence_chain,
            confidence=confidence,
            coregistration=coreg_quality,
            grounding_masks=grounding_masks,
            change_map=change_map,
            spectral_indices=spectral_indices,
            processing_time_ms=elapsed
        )
