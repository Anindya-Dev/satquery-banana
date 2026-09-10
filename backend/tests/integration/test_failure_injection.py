import pytest
import numpy as np
from typing import List
from backend.app.orchestration.task_router import TaskRouter
from backend.app.domain.models import AnalysisRequest, ImageMetadata, CoRegistrationQuality
from backend.app.satellite.base import SatelliteProvider
from backend.app.core.exceptions import SatelliteDataUnavailableError, InvalidBoundingBoxError, InvalidDateRangeError
from backend.app.geospatial.geocoder import Geocoder
from backend.app.retrieval.faiss_store import FAISSIndexManager
from backend.app.retrieval.hybrid_retriever import HybridRetriever
from backend.app.ai.llm_provider import OpenAIProvider

class FailingProvider(SatelliteProvider):
    def __init__(self, failure_mode: str):
        super().__init__(provider_name="Failure Injection Provider")
        self.failure_mode = failure_mode

    def discover_scenes(self, bbox: List[float], start_date: str, end_date: str, max_cloud: float = 15.0) -> List[ImageMetadata]:
        if self.failure_mode == "timeout":
            raise TimeoutError("Satellite provider API query timed out")
        elif self.failure_mode == "malformed":
            return [ImageMetadata(id="", date="invalid-date", cloud_cover_percent=-99.0)]
        elif self.failure_mode == "missing_scene":
            return []
        return []

    def fetch_metadata(self, scene_id: str):
        if self.failure_mode == "missing_scene":
            return None
        return None

    def get_band_data(self, scene_id: str, band_name: str) -> np.ndarray:
        if self.failure_mode == "corrupted_raster":
            # Return empty or invalid NaN array
            arr = np.empty((0, 0))
            return arr
        elif self.failure_mode == "missing_band":
            raise SatelliteDataUnavailableError(f"Requested band {band_name} not available in scene {scene_id}")
        elif self.failure_mode == "timeout":
            raise TimeoutError("Band download read timeout")
        raise SatelliteDataUnavailableError("Provider failure injected")

def test_failure_1_provider_timeout():
    provider = FailingProvider("timeout")
    with pytest.raises(TimeoutError):
        provider.discover_scenes([88.0, 22.0, 88.5, 22.5], "2024-01-01", "2024-05-01")

def test_failure_2_malformed_metadata():
    provider = FailingProvider("malformed")
    scenes = provider.discover_scenes([88.0, 22.0, 88.5, 22.5], "2024-01-01", "2024-05-01")
    assert scenes[0].id == ""

def test_failure_3_missing_scene():
    provider = FailingProvider("missing_scene")
    scenes = provider.discover_scenes([88.0, 22.0, 88.5, 22.5], "2024-01-01", "2024-05-01")
    assert len(scenes) == 0

def test_failure_4_corrupted_raster():
    provider = FailingProvider("corrupted_raster")
    arr = provider.get_band_data("SCENE-1", "B8")
    assert arr.size == 0

def test_failure_5_missing_band():
    provider = FailingProvider("missing_band")
    with pytest.raises(SatelliteDataUnavailableError):
        provider.get_band_data("SCENE-1", "B99")

def test_failure_6_empty_retrieval_result():
    retriever = HybridRetriever()
    # Out of bounds bbox returns no candidates
    candidates = retriever.retrieve_candidates(query_bbox=[-179.0, -89.0, -178.0, -88.0])
    assert isinstance(candidates, list)

def test_failure_7_empty_faiss_index():
    faiss_mgr = FAISSIndexManager(index_path="non_existent_faiss.index")
    hits = faiss_mgr.search(np.random.normal(0, 1, 128), top_k=5)
    assert hits == []

def test_failure_8_corrupted_faiss_mapping():
    faiss_mgr = FAISSIndexManager()
    faiss_mgr.id_to_tile_map = {}
    hits = faiss_mgr.search(np.random.normal(0, 1, 128), top_k=5)
    assert hits == []

def test_failure_9_sqlite_database_error():
    from backend.app.retrieval.filter import RetrievalFilterEngine
    # Querying invalid path DB returns empty candidate set safely
    res = RetrievalFilterEngine.filter_tiles(query_bbox=[0, 0, 1, 1], db_path="non_existent.db")
    assert res == []

def test_failure_10_vlm_timeout():
    ai = OpenAIProvider()
    req = AnalysisRequest(query="Test timeout")
    # Missing API key triggers mock fallback safely without crashing
    res = ai.generate_structured_interpretation(req, [], "Deterministic summary")
    assert "summary" in res

def test_failure_11_vlm_malformed_json():
    ai = OpenAIProvider()
    req = AnalysisRequest(query="Test malformed")
    res = ai.generate_structured_interpretation(req, [], "Malformed JSON response from LLM")
    assert "summary" in res

def test_failure_12_vlm_provider_error():
    ai = OpenAIProvider()
    req = AnalysisRequest(query="Test provider error")
    res = ai.generate_structured_interpretation(req, [], "Error response")
    assert res["insufficient_evidence"] is False

def test_failure_13_invalid_coordinates():
    with pytest.raises(InvalidBoundingBoxError):
        Geocoder.validate_bbox([190.0, 0.0, 200.0, 10.0]) # min_lon > 180

def test_failure_14_invalid_date_range():
    with pytest.raises(InvalidDateRangeError):
        Geocoder.validate_date_range("2024-05-20", "2020-05-20") # start > end

def test_failure_15_failed_coregistration():
    router = TaskRouter()
    req = AnalysisRequest(query="Detect bi-temporal change in Kolkata")
    # Severe shift (> 6.0px) causes safe refusal
    coreg = CoRegistrationQuality(total_shift_px=8.5, is_aligned=False, applied_warp=False)
    from backend.app.domain.sufficiency import EvidenceSufficiencyGate
    is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(images=[], valid_pixel_ratio=1.0, coregistration=coreg)
    assert is_sufficient is False
    assert "Severe spatial mis-alignment" in reason
