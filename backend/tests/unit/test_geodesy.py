from backend.app.geospatial.bbox import SpatialBBoxOps
from backend.app.geospatial.geocoder import Geocoder

def test_haversine_distance():
    # Distance between Kolkata (22.57, 88.36) and Bhubaneswar (20.30, 85.82) is ~360-380 km
    dist = SpatialBBoxOps.haversine_distance_km(22.57, 88.36, 20.30, 85.82)
    assert 340.0 <= dist <= 400.0

def test_calculate_area_sq_km():
    bbox = [88.214, 22.451, 88.482, 22.689]
    area = SpatialBBoxOps.calculate_area_sq_km(bbox)
    assert area > 100.0

def test_geocoder_resolve_and_validate():
    bbox = Geocoder.resolve_location("Kolkata")
    assert len(bbox) == 4
    assert Geocoder.validate_bbox(bbox) is True
