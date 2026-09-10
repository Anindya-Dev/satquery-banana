from typing import List, Dict, Any, Optional
from shapely.geometry import box
from backend.app.storage.metadata_db import MetadataDB

class RetrievalFilterEngine:
    @staticmethod
    def filter_tiles(
        query_bbox: List[float],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_cloud: float = 15.0,
        min_valid_pixels: float = 0.75,
        metadata_db: Optional[MetadataDB] = None,
        db_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Applies hard Spatial -> Temporal -> Quality metadata filtering.
        FAISS semantic search must NEVER bypass or replace this deterministic pre-filter.
        """
        if db_path:
            db = MetadataDB(db_path=db_path)
        else:
            db = metadata_db or MetadataDB()

        candidate_tiles = db.get_tiles(max_cloud=max_cloud, min_valid_pixels=min_valid_pixels)

        if not candidate_tiles:
            return []

        query_geom = box(*query_bbox)
        filtered = []
        for tile in candidate_tiles:
            tile_geom = box(*tile["bbox"])
            if not query_geom.intersects(tile_geom):
                continue
            
            # Temporal range check
            tile_date = tile.get("acquisition_time") or "2024-05-20"
            if start_date and tile_date < start_date:
                continue
            if end_date and tile_date > end_date:
                continue

            filtered.append(tile)

        return filtered
