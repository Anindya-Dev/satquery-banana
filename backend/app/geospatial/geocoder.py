import time
from threading import Lock
from typing import List, Dict, Tuple, Optional
import requests
from shapely.geometry import box
from backend.app.core.exceptions import InvalidGeometryError, InvalidBoundingBoxError, InvalidDateRangeError

# Comprehensive known locations for India and South Asia
KNOWN_GEOLOCATIONS = {
    # West Bengal
    "kolkata": [88.214, 22.451, 88.482, 22.689],
    "howrah": [88.250, 22.590, 88.350, 22.650],
    "hooghly": [87.800, 22.400, 88.100, 23.000],
    "darjeeling": [88.100, 27.000, 88.300, 27.200],
    "medinipur": [86.800, 22.200, 87.500, 22.900],
    
    # Odisha
    "bhubaneswar": [85.780, 20.240, 85.880, 20.350],
    "puri": [85.800, 19.700, 86.000, 20.000],
    "cuttack": [85.800, 20.400, 86.000, 20.600],
    
    # Assam
    "assam": [89.500, 24.500, 96.500, 28.000],
    "guwahati": [91.500, 26.100, 91.700, 26.300],
    "kaziranga": [93.000, 26.400, 93.400, 26.800],
    "brahmaputra": [89.500, 25.500, 96.000, 27.500],
    
    # Tripura
    "tripura": [91.400, 22.500, 92.300, 24.500],
    "manu river": [91.700, 23.500, 91.900, 23.900],
    "manu": [91.700, 23.500, 91.900, 23.900],
    "agartala": [91.280, 23.830, 91.350, 23.920],
    
    # Delhi
    "delhi": [77.080, 28.540, 77.120, 28.580],
    "delhi airport": [77.080, 28.540, 77.120, 28.580],
    "igi airport": [77.080, 28.540, 77.120, 28.580],
    "new delhi": [77.080, 28.540, 77.200, 28.650],
    
    # Maharashtra
    "mumbai": [72.750, 18.900, 73.200, 19.300],
    "pune": [73.700, 18.400, 74.000, 18.700],
    "nagpur": [79.000, 21.100, 79.200, 21.300],
    
    # Western Ghats & Karnataka
    "western ghats": [73.500, 15.000, 74.000, 16.000],
    "bangalore": [77.400, 12.800, 77.700, 13.200],
    "mysore": [76.500, 12.100, 76.800, 12.400],
    "kerala": [74.500, 8.000, 77.500, 12.500],
    
    # Gujarat
    "ahmedabad": [72.400, 22.900, 72.600, 23.100],
    "surat": [72.700, 21.100, 72.900, 21.300],
    "rajkot": [70.500, 22.200, 70.800, 22.500],
    
    # Tamil Nadu
    "chennai": [80.200, 13.000, 80.400, 13.200],
    "coimbatore": [76.900, 11.000, 77.100, 11.200],
    "tamil nadu": [76.500, 8.000, 80.500, 13.500],
    
    # Bihar & Jharkhand
    "patna": [85.000, 25.500, 85.200, 25.700],
    "ranchi": [85.200, 23.200, 85.500, 23.500],
    "bihar": [83.500, 24.500, 87.500, 27.500],
    
    # Uttar Pradesh
    "lucknow": [80.900, 26.800, 81.100, 27.000],
    "varanasi": [82.900, 25.200, 83.100, 25.400],
    "agra": [77.900, 27.100, 78.100, 27.300],
    
    # Madhya Pradesh
    "bhopal": [77.400, 23.200, 77.600, 23.400],
    "indore": [75.800, 22.600, 76.000, 22.800],
    
    # Andhra Pradesh & Telangana
    "hyderabad": [78.300, 17.200, 78.600, 17.500],
    "visakhapatnam": [83.200, 17.600, 83.500, 17.900],
    "vijayawada": [80.600, 16.500, 80.700, 16.600],
    
    # West Bengal - Sundarbans
    "sundarbans": [88.500, 21.500, 89.100, 22.500],
    "sunderbans": [88.500, 21.500, 89.100, 22.500],
    
    # General India
    "india": [68.000, 6.000, 98.000, 36.000],
    "bangladesh": [88.000, 20.500, 92.500, 26.500],
}

class Geocoder:
    _last_request_at = 0.0
    _lock = Lock()
    @staticmethod
    def resolve_location(location_name: str) -> List[float]:
        """
        Resolves location name to [xmin, ymin, xmax, ymax] bounding box in WGS84 (EPSG:4326).
        Falls back to known locations if Nominatim is unavailable.
        """
        loc_lower = location_name.lower().strip()
        
        # First check known locations (fast, no network)
        for key, bbox in KNOWN_GEOLOCATIONS.items():
            if key in loc_lower:
                return bbox

        # Try Nominatim as fallback
        try:
            result = Geocoder.search(location_name, limit=1)
            if result:
                return result[0]["bbox"]
        except InvalidGeometryError:
            pass  # Fall through to error
        
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
