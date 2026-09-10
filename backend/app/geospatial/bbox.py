import math
from typing import List, Dict, Any
from shapely.geometry import box, mapping

class SpatialBBoxOps:
    @staticmethod
    def bbox_to_geojson(bbox: List[float]) -> Dict[str, Any]:
        """
        Converts bbox [xmin, ymin, xmax, ymax] to GeoJSON Polygon geometry.
        """
        xmin, ymin, xmax, ymax = bbox
        geom = box(xmin, ymin, xmax, ymax)
        return mapping(geom)

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes geodesic distance between two lat/lon coordinates in kilometers using Haversine formula."""
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def calculate_area_sq_km(cls, bbox: List[float]) -> float:
        """
        Calculates spatial area in sq km for lat/lon bbox using Haversine geodesic measurements.
        """
        xmin, ymin, xmax, ymax = bbox
        
        # Width at center latitude
        mid_lat = (ymin + ymax) / 2.0
        width_km = cls.haversine_distance_km(mid_lat, xmin, mid_lat, xmax)
        
        # Height along meridian
        height_km = cls.haversine_distance_km(ymin, xmin, ymax, xmin)
        
        return float(round(width_km * height_km, 3))
