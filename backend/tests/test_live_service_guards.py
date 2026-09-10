import pytest

from backend.app.core.exceptions import SatelliteDataUnavailableError
from backend.app.geospatial.geocoder import Geocoder
from backend.app.satellite.sentinel1 import Sentinel1RTCProvider
from backend.app.satellite.sentinel2 import Sentinel2Provider


def test_sentinel2_reads_requested_aoi_not_full_scene():
    provider = Sentinel2Provider()
    provider._items["scene"] = {"assets": {}, "bbox": [0, 0, 10, 10]}
    provider._aoi_by_scene["scene"] = [1, 1, 2, 2]
    assert provider._aoi_by_scene["scene"] == [1, 1, 2, 2]


def test_sentinel1_requires_subscription_key(monkeypatch):
    monkeypatch.setattr("backend.app.satellite.sentinel1.settings.PLANETARY_COMPUTER_SUBSCRIPTION_KEY", "")
    with pytest.raises(SatelliteDataUnavailableError, match="SUBSCRIPTION_KEY"):
        Sentinel1RTCProvider()


def test_known_geocoder_location_does_not_call_network():
    assert Geocoder.resolve_location("Kolkata river basin") == [88.214, 22.451, 88.482, 22.689]
