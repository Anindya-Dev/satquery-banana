import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.retrieval.filter import RetrievalFilterEngine
from backend.app.retrieval.faiss_store import FAISSIndexManager
from backend.app.core.config import settings
from backend.app.core.logging import logger

class HybridRetriever:
    SEMANTIC_RERANK_MODE = settings.SEMANTIC_RERANK_MODE

    def __init__(self, faiss_manager: Optional[FAISSIndexManager] = None):
        self.faiss_manager = faiss_manager or FAISSIndexManager()

    def retrieve_candidates(
        self,
        query_bbox: List[float],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_cloud: float = 15.0,
        min_valid_pixels: float = 0.75
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval workflow:
        1. Hard Spatial + Temporal + Quality Filter (Metadata DB) - Authoritative candidate set
        2. FAISS Semantic Re-ranking (Currently MOCKED_SEMANTIC_RERANK using mock vector embeddings)
        """
        # Step 1: Authoritative Deterministic Filter
        candidates = RetrievalFilterEngine.filter_tiles(
            query_bbox=query_bbox,
            start_date=start_date,
            end_date=end_date,
            max_cloud=max_cloud,
            min_valid_pixels=min_valid_pixels
        )

        if not candidates:
            return []

        # Step 2: Semantic Re-ranking via FAISS (MOCKED_SEMANTIC_RERANK)
        logger.debug(f"FAISS Semantic Reranking status: {self.SEMANTIC_RERANK_MODE}")
        query_vector = np.random.normal(0, 1, 128)
        faiss_hits = self.faiss_manager.search(query_vector, top_k=len(candidates))
        
        if faiss_hits:
            hit_map = {tile_id: score for tile_id, score in faiss_hits}
            candidates.sort(key=lambda t: hit_map.get(t["tile_id"], 999.0))

        return candidates
