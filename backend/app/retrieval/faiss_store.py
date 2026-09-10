import json
import os
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

class FAISSIndexManager:
    def __init__(self, dimension: int = 128, index_path: Optional[str] = None, map_path: Optional[str] = None):
        self.dimension = dimension
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.map_path = map_path or settings.FAISS_MAP_PATH
        self.vector_map: Dict[int, str] = {} # vector_id -> tile_id
        self.index = None
        self._init_index()

    def _init_index(self):
        if not HAS_FAISS:
            logger.info("FAISS library not installed. Vector search fallback mode enabled.")
            return

        if os.path.exists(self.index_path) and os.path.exists(self.map_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.map_path, "r") as f:
                    self.vector_map = {int(k): v for k, v in json.load(f).items()}
                logger.info("FAISS index loaded successfully.", n_vectors=self.index.ntotal)
            except Exception as e:
                logger.warning(f"Failed to load FAISS index from disk ({str(e)}). Re-initializing empty index.")
                self.index = faiss.IndexFlatL2(self.dimension)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

    def add_vectors(self, tile_ids: List[str], vectors: np.ndarray):
        if not HAS_FAISS or self.index is None:
            return

        start_id = self.index.ntotal
        self.index.add(vectors.astype(np.float32))

        for idx, t_id in enumerate(tile_ids):
            vec_id = start_id + idx
            self.vector_map[vec_id] = t_id

        self._save()

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        if not HAS_FAISS or self.index is None or self.index.ntotal == 0:
            return []

        distances, indices = self.index.search(query_vector.reshape(1, -1).astype(np.float32), top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx in self.vector_map:
                tile_id = self.vector_map[idx]
                results.append((tile_id, float(dist)))

        return results

    def _save(self):
        if not HAS_FAISS or self.index is None:
            return

        faiss.write_index(self.index, self.index_path)
        with open(self.map_path, "w") as f:
            json.dump(self.vector_map, f)

    def rebuild_index(self, tiles_data: List[Dict[str, Any]]):
        """Rebuilds FAISS index completely from canonical metadata store records."""
        if not HAS_FAISS:
            return

        self.index = faiss.IndexFlatL2(self.dimension)
        self.vector_map.clear()

        tile_ids = []
        vectors = []

        for tile in tiles_data:
            t_id = tile["tile_id"]
            # Generate deterministic synthetic embedding vector from stats
            np.random.seed(abs(hash(t_id)) % (2**32 - 1))
            vec = np.random.normal(0, 1, self.dimension)
            tile_ids.append(t_id)
            vectors.append(vec)

        if tile_ids:
            self.add_vectors(tile_ids, np.array(vectors))

faiss_manager = FAISSIndexManager()
