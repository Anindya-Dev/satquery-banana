from datetime import date, timedelta
import re
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
    start_date: str
    end_date: str

class QueryParser:
    @classmethod
    def parse_intent(cls, request: AnalysisRequest) -> StructuredQuery:
        query_lower = request.query.lower()
        
        # 1. Resolve Location
        bbox = request.bbox or Geocoder.resolve_location(query_lower)
        Geocoder.validate_bbox(bbox)
        start_date, end_date = cls._parse_dates(request, query_lower)

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
            task_type=task_type,
            start_date=start_date,
            end_date=end_date,
        )

    @classmethod
    def classify_task(cls, request: AnalysisRequest) -> TaskType:
        return cls.parse_intent(request).task_type

    @staticmethod
    def _parse_dates(request: AnalysisRequest, query_lower: str) -> tuple[str, str]:
        if request.start_date and request.end_date:
            Geocoder.validate_date_range(request.start_date, request.end_date)
            return request.start_date, request.end_date

        years = [int(year) for year in re.findall(r"\\b(19\\d{2}|20\\d{2})\\b", query_lower)]
        if len(years) >= 2:
            start_year, end_year = min(years), max(years)
            return f"{start_year}-01-01T00:00:00Z", f"{end_year}-12-31T23:59:59Z"
        if len(years) == 1:
            year = years[0]
            return f"{year}-01-01T00:00:00Z", f"{year}-12-31T23:59:59Z"

        end = date.today()
        start = end - timedelta(days=90)
        return f"{start.isoformat()}T00:00:00Z", f"{end.isoformat()}T23:59:59Z"
