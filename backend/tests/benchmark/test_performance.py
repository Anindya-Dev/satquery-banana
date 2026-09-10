import pytest
import time
import numpy as np
from backend.app.understanding.query_parser import QueryParser
from backend.app.geospatial.geocoder import Geocoder
from backend.app.retrieval.hybrid_retriever import HybridRetriever
from backend.app.geospatial.raster_ops import RasterOps
from backend.app.orchestration.task_router import TaskRouter
from backend.app.domain.models import AnalysisRequest

def measure_percentiles(durations_ms):
    return {
        "P50": float(np.percentile(durations_ms, 50)),
        "P95": float(np.percentile(durations_ms, 95)),
        "P99": float(np.percentile(durations_ms, 99))
    }

def test_query_parsing_performance():
    req = AnalysisRequest(query="Calculate NDVI across Kolkata coastal zones")
    durations = []
    for _ in range(50):
        t0 = time.perf_counter()
        _ = QueryParser.parse_intent(req)
        durations.append((time.perf_counter() - t0) * 1000)
    
    stats = measure_percentiles(durations)
    assert stats["P50"] < 5.0 # < 5 ms P50 target

def test_retrieval_performance():
    retriever = HybridRetriever()
    bbox = [88.214, 22.451, 88.482, 22.689]
    durations = []
    for _ in range(50):
        t0 = time.perf_counter()
        _ = retriever.retrieve_candidates(query_bbox=bbox)
        durations.append((time.perf_counter() - t0) * 1000)
        
    stats = measure_percentiles(durations)
    assert stats["P50"] < 10.0 # < 10 ms P50 target

def test_raster_math_512x512_performance():
    nir = np.random.uniform(0.3, 0.7, (512, 512)).astype(np.float32)
    red = np.random.uniform(0.1, 0.3, (512, 512)).astype(np.float32)
    durations = []
    for _ in range(50):
        t0 = time.perf_counter()
        _ = RasterOps.calculate_ndvi(nir, red)
        durations.append((time.perf_counter() - t0) * 1000)
        
    stats = measure_percentiles(durations)
    assert stats["P50"] < 5.0 # < 5 ms P50 target for 512x512 array

def test_large_raster_2048x2048_performance():
    nir = np.random.uniform(0.3, 0.7, (2048, 2048)).astype(np.float32)
    red = np.random.uniform(0.1, 0.3, (2048, 2048)).astype(np.float32)
    t0 = time.perf_counter()
    _ = RasterOps.calculate_ndvi(nir, red)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 300.0 # < 300 ms target for 4MP array

def test_end_to_end_pipeline_performance():
    router = TaskRouter()
    req = AnalysisRequest(query="Calculate NDVI across Kolkata coastal zones")
    durations = []
    for _ in range(10):
        t0 = time.perf_counter()
        _ = router.process(req)
        durations.append((time.perf_counter() - t0) * 1000)
        
    stats = measure_percentiles(durations)
    assert stats["P50"] < 250.0 # < 250 ms P50 end-to-end execution target
