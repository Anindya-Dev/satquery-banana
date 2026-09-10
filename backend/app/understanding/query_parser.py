from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.domain.models import TaskType, AnalysisRequest
from backend.app.geospatial.geocoder import Geocoder

class StructuredQuery(BaseModel):
    raw_query: str
    location_text: str = Field(default="Kolkata")
    query_bbox: List[float] = Field(default_factory=lambda: [88.214, 22.451, 88.482, 22.689])
    time_range_days: int = Field(default=30)
    phenomenon: str = Field(default="water_inundation")
    requested_indices: List[str] = Field(default_factory=lambda: ["NDWI", "NDVI"])
    task_type: TaskType = Field(default=TaskType.VQA)

class QueryParser:
    @classmethod
    def parse_intent(cls, request: AnalysisRequest) -> StructuredQuery:
        query_lower = request.query.lower()
        
        # 1. Resolve Location
        bbox = Geocoder.resolve_location(query_lower)

        # 2. Parse Task Type & Requested Indices
        task_type = request.task_type
        if not task_type or task_type == TaskType.AUTO_CLASSIFIED:
            if any(w in query_lower for w in ["change", "compare", "flood", "bitemporal", "inundation", "before and after", "2020", "2024", "delta"]):
                task_type = TaskType.CHANGE_DETECTION
            elif any(w in query_lower for w in ["segment", "locate", "bbox", "outline", "aircraft", "runway", "building", "field", "boundaries"]):
                task_type = TaskType.GROUNDING
            elif any(w in query_lower for w in ["sar", "sentinel-1", "cloud", "radar", "speckle", "all-weather", "fusion", "night"]):
                task_type = TaskType.OPTICAL_SAR_FUSION
            else:
                task_type = TaskType.VQA

        # 3. Derive Indices
        indices = ["NDVI", "NDWI"]
        if task_type == TaskType.CHANGE_DETECTION or "water" in query_lower:
            indices = ["NDWI", "MNDWI"]
        elif "building" in query_lower or "urban" in query_lower:
            indices = ["NDBI"]
        elif "burn" in query_lower or "fire" in query_lower:
            indices = ["NBR"]

        return StructuredQuery(
            raw_query=request.query,
            location_text="Resolved Region",
            query_bbox=bbox,
            time_range_days=30,
            phenomenon="remote_sensing_phenomenon",
            requested_indices=indices,
            task_type=task_type
        )

    @classmethod
    def classify_task(cls, request: AnalysisRequest) -> TaskType:
        return cls.parse_intent(request).task_type
