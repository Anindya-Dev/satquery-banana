import time
from threading import Lock
from typing import List, Dict, Tuple, Optional
import requests
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
    _last_request_at = 0.0
    _lock = Lock()
    @staticmethod
    def resolve_location(location_name: str) -> List[float]:
        """
        Resolves location name to [xmin, ymin, xmax, ymax] bounding box in WGS84 (EPSG:4326).
        """
        loc_lower = location_name.lower().strip()
        for key, bbox in KNOWN_GEOLOCATIONS.items():
            if key in loc_lower:
                return bbox

        result = Geocoder.search(location_name, limit=1)
        if result:
            return result[0]["bbox"]
        raise InvalidGeometryError(f"Could not resolve a geographic area from '{location_name}'. Supply an explicit bbox.")

    @classmethod
    def search(cls, place: str, limit: int = 5) -> List[Dict[str, object]]:
        """Public Nominatim search with the service's required user agent and one-request-per-second pacing."""
        from backend.app.core.config import settings
        with cls._lock:
            remaining = settings.NOMINATIM_MIN_INTERVAL_SECONDS - (time.monotonic() - cls._last_request_at)
            if remaining > 0:
                time.sleep(remaining)
            try:
                response = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": place, "format": "jsonv2", "limit": min(limit, 5)},
                    headers={"User-Agent": settings.NOMINATIM_USER_AGENT},
                    timeout=15,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                raise InvalidGeometryError(f"Geocoding service is unavailable: {exc}") from exc
            finally:
                cls._last_request_at = time.monotonic()

        results = []
        for item in response.json():
            south, north, west, east = map(float, item["boundingbox"])
            results.append({"name": item["display_name"], "bbox": [west, south, east, north]})
        return results

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
