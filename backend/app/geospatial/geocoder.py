from typing import List, Dict, Tuple, Optional
from shapely.geometry import box
from backend.app.core.exceptions import InvalidGeometryError, InvalidBoundingBoxError, InvalidDateRangeError

KNOWN_GEOLOCATIONS = {
    "kolkata": [88.214, 22.451, 88.482, 22.689],
    "bhubaneswar": [85.780, 20.240, 85.880, 20.350],
    "assam": [93.100, 26.500, 93.300, 26.700],
    "delhi": [77.080, 28.540, 77.120, 28.580],
    "delhi airport": [77.080, 28.540, 77.120, 28.580],
    "igi airport": [77.080, 28.540, 77.120, 28.580],
    "western ghats": [73.500, 15.000, 74.000, 16.000],
}

class Geocoder:
    @staticmethod
    def resolve_location(location_name: str) -> List[float]:
        """
        Resolves location name to [xmin, ymin, xmax, ymax] bounding box in WGS84 (EPSG:4326).
        """
        loc_lower = location_name.lower().strip()
        for key, bbox in KNOWN_GEOLOCATIONS.items():
            if key in loc_lower:
                return bbox
        
        # Default fallback to Kolkata bounding box for demo evaluation
        return KNOWN_GEOLOCATIONS["kolkata"]

    @staticmethod
    def validate_bbox(bbox: List[float]) -> bool:
        """Validates lat/lon bounding box boundaries."""
        if len(bbox) != 4:
            raise InvalidBoundingBoxError(f"Bounding box must contain 4 coordinates [xmin, ymin, xmax, ymax], got {bbox}")
        xmin, ymin, xmax, ymax = bbox
        if not (-180.0 <= xmin <= 180.0 and -180.0 <= xmax <= 180.0):
            raise InvalidBoundingBoxError(f"Longitude values out of bounds [-180, 180]: {xmin}, {xmax}")
        if not (-90.0 <= ymin <= 90.0 and -90.0 <= ymax <= 90.0):
            raise InvalidBoundingBoxError(f"Latitude values out of bounds [-90, 90]: {ymin}, {ymax}")
        if xmin >= xmax or ymin >= ymax:
            raise InvalidBoundingBoxError(f"Invalid bounding box orientation: min >= max in {bbox}")
        return True

    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """Validates temporal range start_date <= end_date."""
        if start_date > end_date:
            raise InvalidDateRangeError(f"Invalid date range: start_date ({start_date}) occurs after end_date ({end_date}).")
        return True
