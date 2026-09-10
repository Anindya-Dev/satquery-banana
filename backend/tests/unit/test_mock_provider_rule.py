import pytest
from backend.app.satellite.sentinel2 import Sentinel2Provider
from backend.app.core.exceptions import SatelliteDataUnavailableError
from backend.app.core.config import settings

def test_sentinel2_provider_raises_error_without_mock_fallback():
    provider = Sentinel2Provider()
    with pytest.raises(SatelliteDataUnavailableError) as exc_info:
        provider.get_band_data("S2A_MSIL2A_REAL_SCENE", "B8")
    assert "Live Copernicus download" in str(exc_info.value)

def test_specialists_require_provider_or_use_explicit_mock():
    from backend.app.specialists.vqa import VQASpecialist
    from backend.app.domain.models import AnalysisRequest
    from backend.app.domain.evidence import EvidenceCollector
    
    spec = VQASpecialist()
    req = AnalysisRequest(query="Test vegetation index")
    collector = EvidenceCollector()
    
    # Passing real Sentinel2Provider should raise error rather than silently fallback
    real_provider = Sentinel2Provider()
    with pytest.raises(SatelliteDataUnavailableError):
        spec.execute(req, collector, provider=real_provider, scene_id="REAL_SCENE_123")
