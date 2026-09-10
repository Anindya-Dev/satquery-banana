import pytest
import numpy as np
from typing import List, Dict, Any
from backend.app.retrieval.filter import RetrievalFilterEngine
from backend.app.retrieval.hybrid_retriever import HybridRetriever
from backend.app.retrieval.faiss_store import FAISSIndexManager
from backend.app.core.config import settings

def test_deterministic_retrieval_spatial_correctness():
    # Kolkata bbox
    bbox = [88.214, 22.451, 88.482, 22.689]
    candidates = RetrievalFilterEngine.filter_tiles(query_bbox=bbox, max_cloud=15.0, min_valid_pixels=0.75)
    assert len(candidates) > 0
    assert candidates[0]["tile_id"] == "TILE-KOLKATA-001"

def test_deterministic_retrieval_quality_filtering_rejects_cloudy():
    bbox = [88.214, 22.451, 88.482, 22.689]
    # Set max_cloud to 1% to reject 3.2% cloud tile
    candidates = RetrievalFilterEngine.filter_tiles(query_bbox=bbox, max_cloud=1.0, min_valid_pixels=0.75)
    assert len(candidates) == 0

def test_deterministic_retrieval_temporal_filtering():
    bbox = [88.214, 22.451, 88.482, 22.689]
    # Match valid temporal range
    valid_candidates = RetrievalFilterEngine.filter_tiles(query_bbox=bbox, start_date="2024-05-01", end_date="2024-05-31")
    assert len(valid_candidates) > 0
    
    # Out of range temporal query
    invalid_candidates = RetrievalFilterEngine.filter_tiles(query_bbox=bbox, start_date="2018-01-01", end_date="2018-01-31")
    assert len(invalid_candidates) == 0

def test_faiss_retrieval_metrics_evaluation():
    """
    Evaluates retrieval metrics over a golden dataset.
    Note: Explicitly tags SEMANTIC_RERANK_MODE = MOCKED_SEMANTIC_RERANK
    """
    retriever = HybridRetriever()
    assert retriever.SEMANTIC_RERANK_MODE == "MOCKED_SEMANTIC_RERANK"

    golden_dataset = [
        {"query_bbox": [88.214, 22.451, 88.482, 22.689], "expected_tile": "TILE-KOLKATA-001"},
        {"query_bbox": [85.780, 20.240, 85.880, 20.350], "expected_tile": "TILE-BHUBANESWAR-001"},
        {"query_bbox": [93.100, 26.500, 93.300, 26.700], "expected_tile": "TILE-ASSAM-SAR-001"},
        {"query_bbox": [77.080, 28.540, 77.120, 28.580], "expected_tile": "TILE-DELHI-001"}
    ]

    recalls_at_1 = []
    recalls_at_5 = []
    mrr_list = []

    for item in golden_dataset:
        candidates = retriever.retrieve_candidates(query_bbox=item["query_bbox"])
        retrieved_ids = [c["tile_id"] for c in candidates]
        
        # Calculate Recall@1, Recall@5, MRR
        r1 = 1.0 if (retrieved_ids and retrieved_ids[0] == item["expected_tile"]) else 0.0
        r5 = 1.0 if item["expected_tile"] in retrieved_ids[:5] else 0.0
        
        mrr = 0.0
        if item["expected_tile"] in retrieved_ids:
            rank = retrieved_ids.index(item["expected_tile"]) + 1
            mrr = 1.0 / rank

        recalls_at_1.append(r1)
        recalls_at_5.append(r5)
        mrr_list.append(mrr)

    mean_recall_1 = np.mean(recalls_at_1)
    mean_recall_5 = np.mean(recalls_at_5)
    mean_mrr = np.mean(mrr_list)

    # In deterministic filtering, all target golden items are returned in candidate set
    assert mean_recall_1 >= 0.75
    assert mean_recall_5 == 1.0
    assert mean_mrr >= 0.75
