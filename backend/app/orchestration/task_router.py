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
from backend.app.satellite.sentinel2 import Sentinel2Provider
from backend.app.satellite.sentinel1 import Sentinel1RTCProvider
from backend.app.retrieval.hybrid_retriever import HybridRetriever
from backend.app.ai.llm_provider import OpenAIProvider
from backend.app.specialists.vqa import VQASpecialist
from backend.app.specialists.grounding import GroundingSpecialist
from backend.app.specialists.change_detection import ChangeDetectionSpecialist
from backend.app.specialists.optical_sar_fusion import OpticalSARFusionSpecialist
from backend.app.core.logging import logger

class TaskRouter:
    def __init__(self, satellite_provider: Optional[SatelliteProvider] = None):
        self.satellite_provider = satellite_provider or Sentinel2Provider()
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
        request.bbox = structured_query.query_bbox

        # Layer 4 & 5: Authoritative live STAC retrieval and pixel-quality check.
        provider = Sentinel1RTCProvider() if task_type == TaskType.OPTICAL_SAR_FUSION else self.satellite_provider
        scenes = provider.discover_scenes(
            bbox=structured_query.query_bbox,
            start_date=structured_query.start_date,
            end_date=structured_query.end_date,
            max_cloud=15.0,
        )
        if not scenes:
            raise InsufficientEvidenceError(
                "No Sentinel-2 Level-2A scene met the requested area, dates, and cloud-cover threshold."
            )

        scenes_by_date = sorted(scenes, key=lambda scene: scene.date)
        sample_img = scenes_by_date[-1] if task_type == TaskType.CHANGE_DETECTION else scenes[0]
        comparison_img = scenes_by_date[0] if task_type == TaskType.CHANGE_DETECTION else None
        if task_type == TaskType.CHANGE_DETECTION and comparison_img.id == sample_img.id:
            raise InsufficientEvidenceError(
                "Change detection needs two distinct cloud-valid Sentinel-2 acquisitions in the requested date range."
            )
        valid_pixel_ratio = provider.get_valid_pixel_ratio(sample_img.id)
        
        # Layer 6: Spatial Alignment Check for Change Detection
        coreg_quality = None
        if task_type == TaskType.CHANGE_DETECTION:
            t1_img = provider.get_band_data(comparison_img.id, "B4")
            t2_img = provider.get_band_data(sample_img.id, "B4")
            coreg_quality = CoRegistrationEngine.evaluate_alignment(t1_img, t2_img)

        # Layer 7: Pre-VLM Evidence Sufficiency & Safety Refusal Gate
        is_refused, refusal_reason = RefusalEngine.evaluate_gates(
            query=request.query,
            images=[sample_img],
            valid_pixel_ratio=valid_pixel_ratio,
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
                confidence=ConfidenceScorer.calculate(valid_pixel_ratio=valid_pixel_ratio, cloud_percent=sample_img.cloud_cover_percent),
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
                request, evidence_collector, provider=provider, scene_id=sample_img.id,
                comparison_scene_id=comparison_img.id
            )
        elif task_type == TaskType.GROUNDING:
            answer_text, grounding_masks, change_map, spectral_indices = self.grounding_specialist.execute(
                request, evidence_collector, provider=provider, scene_id=sample_img.id
            )
        elif task_type == TaskType.OPTICAL_SAR_FUSION:
            answer_text, grounding_masks, change_map, spectral_indices = self.fusion_specialist.execute(
                request, evidence_collector, provider=provider, scene_id=sample_img.id
            )
        else:
            answer_text, grounding_masks, change_map, spectral_indices = self.vqa_specialist.execute(
                request, evidence_collector, provider=provider, scene_id=sample_img.id
            )

        evidence_chain = evidence_collector.get_all()

        # Layer 10: AI Provider Interpretation & Claim Validation
        vlm_res = self.ai_provider.generate_structured_interpretation(request, evidence_chain, answer_text)
        grounded_answer = ClaimValidator.validate_and_ground(vlm_res["summary"], evidence_chain)

        # Layer 11: Deterministic Confidence Calculation
        confidence = ConfidenceScorer.calculate(
            valid_pixel_ratio=valid_pixel_ratio,
            cloud_percent=sample_img.cloud_cover_percent,
            coregistration=coreg_quality,
            spectral_sane=True
        )

        elapsed = float(round((time.time() - start_time) * 1000, 2))
        preview_provider = provider if isinstance(provider, Sentinel2Provider) and task_type != TaskType.OPTICAL_SAR_FUSION else None
        primary_preview = preview_provider.get_rgb_preview(sample_img.id) if preview_provider else None
        secondary_preview = preview_provider.get_rgb_preview(comparison_img.id) if preview_provider and comparison_img else None

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
            image_primary_url=primary_preview,
            image_secondary_url=secondary_preview,
            scene_dates=[scene.date for scene in [comparison_img, sample_img] if scene],
            processing_time_ms=elapsed
        )
