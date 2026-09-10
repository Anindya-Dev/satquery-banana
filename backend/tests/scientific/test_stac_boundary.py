"""
SatQuery AI — STAC Integration Boundary Tests
==============================================
PHASE 4: Sentinel2Provider Boundary Contract Verification

These tests verify the CRITICAL boundary between the mock-based
development pipeline and the real Sentinel-2 data pipeline.

Key invariants (non-negotiable architectural rules):
  1. Sentinel2Provider.get_band_data() MUST raise SatelliteDataUnavailableError
     when credentials are absent. It must NEVER silently return fake data.
  2. Sentinel2Provider.discover_scenes() returns valid ImageMetadata models.
  3. MockSatelliteProvider.get_band_data() must NEVER raise for any registered band.
  4. Both providers share the identical abstract interface (Liskov Substitution Principle).
  5. Any specialist receiving a real provider without credentials must propagate
     the SatelliteDataUnavailableError cleanly, not swallow it.

These tests CANNOT verify live STAC queries (no credentials in CI environment).
What they DO verify is the safety contract: the system never pretends
to have real data when it does not.
"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from backend.app.satellite.base import SatelliteProvider
from backend.app.satellite.sentinel2 import Sentinel2Provider
from backend.app.satellite.mock_provider import MockSatelliteProvider
from backend.app.core.exceptions import SatelliteDataUnavailableError
from backend.app.domain.models import ImageMetadata, SensorType


# ─────────────────────────────────────────────────────────────────────────────
# SAFETY CONTRACT 1: Sentinel2Provider must raise on get_band_data
# ─────────────────────────────────────────────────────────────────────────────
class TestSentinel2ProviderSafetyContract:
    """
    Verifies that Sentinel2Provider never silently returns mock data.
    Any call to get_band_data MUST raise SatelliteDataUnavailableError.
    """

    def setup_method(self):
        self.provider = Sentinel2Provider()

    def test_get_band_data_raises_unavailable_without_credentials(self):
        """
        CRITICAL SAFETY: No credentials → SatelliteDataUnavailableError.
        Never silently falls back to mock arrays.
        """
        with pytest.raises(SatelliteDataUnavailableError) as exc_info:
            self.provider.get_band_data("S2A_TEST_SCENE", "B8")

        assert "credentials" in str(exc_info.value).lower() or "mock" in str(exc_info.value).lower(), (
            "Exception message must explain why data is unavailable (credentials/mock hint)."
        )

    def test_get_band_data_raises_for_all_major_bands(self):
        """All primary Sentinel-2 bands must raise, not return fake arrays."""
        bands = ["B2", "B3", "B4", "B8", "B11", "B12"]
        for band in bands:
            with pytest.raises(SatelliteDataUnavailableError):
                self.provider.get_band_data("S2A_SCENE_001", band)

    def test_discover_scenes_returns_valid_metadata(self):
        """discover_scenes must return valid ImageMetadata objects (STAC stub)."""
        scenes = self.provider.discover_scenes(
            bbox=[88.214, 22.451, 88.482, 22.689],
            start_date="2024-05-01",
            end_date="2024-05-31",
            max_cloud=15.0
        )
        assert isinstance(scenes, list), "discover_scenes must return a list"
        assert len(scenes) >= 1, "discover_scenes stub must return at least one scene"
        for scene in scenes:
            assert isinstance(scene, ImageMetadata), (
                f"discover_scenes returned non-ImageMetadata object: {type(scene)}"
            )
            assert scene.id, "Scene must have a non-empty ID"
            assert 0.0 <= scene.cloud_cover_percent <= 100.0

    def test_fetch_metadata_returns_valid_model(self):
        """fetch_metadata must return a valid ImageMetadata object (STAC stub)."""
        meta = self.provider.fetch_metadata("S2A_MSIL2A_20240520T050641_N0510_R019_T45QXE")
        assert isinstance(meta, ImageMetadata)
        assert meta.sensor == SensorType.OPTICAL_SENTINEL2

    def test_provider_name_is_descriptive(self):
        """Provider name must be informative for logging/evidence chain attribution."""
        assert len(self.provider.provider_name) > 5, (
            f"Provider name too short: '{self.provider.provider_name}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SAFETY CONTRACT 2: MockSatelliteProvider contract
# ─────────────────────────────────────────────────────────────────────────────
class TestMockProviderContract:
    """
    Verifies MockSatelliteProvider always returns valid data for all registered scenes.
    """

    def setup_method(self):
        self.provider = MockSatelliteProvider()

    def test_get_band_data_never_raises_for_registered_scenes(self):
        """MockSatelliteProvider must never raise for any known scene+band combo."""
        scenes = ["SCENE-KOLKATA-2024", "SCENE-BHUBANESWAR-2023", "SCENE-ASSAM-SAR-2024"]
        bands  = ["B3", "B4", "B8", "B11", "VV", "VH"]
        for scene_id in scenes:
            for band in bands:
                result = self.provider.get_band_data(scene_id, band)
                assert isinstance(result, np.ndarray), (
                    f"Expected ndarray for {scene_id}/{band}, got {type(result)}"
                )
                assert result.size > 0, f"Empty array for {scene_id}/{band}"
                assert not np.isnan(result).any(), f"NaN in mock data {scene_id}/{band}"

    def test_mock_band_values_in_physical_range(self):
        """
        Mock reflectance bands must return values in physically plausible L2A range [0, 1].
        VV/VH SAR bands are allowed to be in linear power domain (may exceed 1).
        """
        optical_bands = ["B3", "B4", "B8", "B11"]
        for band in optical_bands:
            data = self.provider.get_band_data("SCENE-KOLKATA-2024", band)
            assert float(np.min(data)) >= 0.0, f"Negative reflectance for band {band}"
            assert float(np.max(data)) <= 1.0, f"Reflectance > 1.0 for band {band}: max={float(np.max(data))}"

    def test_mock_determinism_same_scene_same_band(self):
        """
        MockSatelliteProvider must be deterministic: same scene+band → same array.
        This is required for reproducible test results.
        """
        r1 = self.provider.get_band_data("SCENE-KOLKATA-2024", "B8")
        r2 = self.provider.get_band_data("SCENE-KOLKATA-2024", "B8")
        np.testing.assert_array_equal(r1, r2, err_msg=(
            "MockSatelliteProvider returned different arrays for same scene+band. "
            "Mock data must be deterministic."
        ))

    def test_mock_different_bands_produce_different_arrays(self):
        """Different spectral bands must return distinct data (realistic simulation)."""
        nir  = self.provider.get_band_data("SCENE-KOLKATA-2024", "B8")
        red  = self.provider.get_band_data("SCENE-KOLKATA-2024", "B4")
        green = self.provider.get_band_data("SCENE-KOLKATA-2024", "B3")

        assert not np.array_equal(nir, red),   "B8 NIR and B4 Red must differ"
        assert not np.array_equal(nir, green),  "B8 NIR and B3 Green must differ"
        assert not np.array_equal(red, green),  "B4 Red and B3 Green must differ"

    def test_discover_scenes_returns_list_of_metadata(self):
        """discover_scenes must return a filtered list of ImageMetadata."""
        scenes = self.provider.discover_scenes(
            bbox=[88.0, 22.0, 89.0, 23.0],
            start_date="2024-01-01",
            end_date="2024-12-31",
            max_cloud=15.0
        )
        assert isinstance(scenes, list)
        for scene in scenes:
            assert isinstance(scene, ImageMetadata)


# ─────────────────────────────────────────────────────────────────────────────
# SAFETY CONTRACT 3: Liskov Substitution Principle — both providers must
# satisfy the abstract interface identically
# ─────────────────────────────────────────────────────────────────────────────
class TestProviderLiskovSubstitution:
    """
    Verifies both providers implement the SatelliteProvider contract.
    """

    def test_sentinel2_inherits_from_base(self):
        assert isinstance(Sentinel2Provider(), SatelliteProvider)

    def test_mock_inherits_from_base(self):
        assert isinstance(MockSatelliteProvider(), SatelliteProvider)

    def test_both_providers_have_required_methods(self):
        required_methods = ["discover_scenes", "fetch_metadata", "get_band_data"]
        for provider_cls in [Sentinel2Provider, MockSatelliteProvider]:
            provider = provider_cls()
            for method in required_methods:
                assert hasattr(provider, method), (
                    f"{provider_cls.__name__} missing required method: {method}"
                )
                assert callable(getattr(provider, method)), (
                    f"{provider_cls.__name__}.{method} is not callable"
                )

    def test_provider_name_attribute_required(self):
        """Both providers must expose provider_name for evidence chain attribution."""
        s2 = Sentinel2Provider()
        mock = MockSatelliteProvider()
        assert isinstance(s2.provider_name, str) and s2.provider_name
        assert isinstance(mock.provider_name, str) and mock.provider_name


# ─────────────────────────────────────────────────────────────────────────────
# SAFETY CONTRACT 4: Specialist propagation of SatelliteDataUnavailableError
# ─────────────────────────────────────────────────────────────────────────────
class TestSpecialistPropagatesProviderError:
    """
    When a real provider raises SatelliteDataUnavailableError,
    specialists must NOT catch and silence it.
    """

    def _make_failing_provider(self):
        """Creates a SatelliteProvider mock that always raises on get_band_data."""
        provider = MagicMock(spec=SatelliteProvider)
        provider.provider_name = "FailingTestProvider"
        provider.get_band_data.side_effect = SatelliteDataUnavailableError(
            "Simulated credential failure: real data unavailable."
        )
        return provider

    def test_vqa_specialist_propagates_provider_error(self):
        from backend.app.specialists.vqa import VQASpecialist
        from backend.app.domain.models import AnalysisRequest
        from backend.app.domain.evidence import EvidenceCollector

        specialist = VQASpecialist()
        failing_provider = self._make_failing_provider()

        with pytest.raises(SatelliteDataUnavailableError):
            specialist.execute(
                request=AnalysisRequest(query="Analyze vegetation in Kolkata"),
                evidence_collector=EvidenceCollector(),
                provider=failing_provider,
                scene_id="S2_REAL_SCENE_MISSING"
            )

    def test_change_detection_specialist_propagates_provider_error(self):
        from backend.app.specialists.change_detection import ChangeDetectionSpecialist
        from backend.app.domain.models import AnalysisRequest
        from backend.app.domain.evidence import EvidenceCollector

        specialist = ChangeDetectionSpecialist()
        failing_provider = self._make_failing_provider()

        with pytest.raises(SatelliteDataUnavailableError):
            specialist.execute(
                request=AnalysisRequest(query="Detect flood change in Assam"),
                evidence_collector=EvidenceCollector(),
                provider=failing_provider,
                scene_id="S2_REAL_SCENE_MISSING"
            )

    def test_sar_fusion_specialist_propagates_provider_error(self):
        from backend.app.specialists.optical_sar_fusion import OpticalSARFusionSpecialist
        from backend.app.domain.models import AnalysisRequest
        from backend.app.domain.evidence import EvidenceCollector

        specialist = OpticalSARFusionSpecialist()
        failing_provider = self._make_failing_provider()

        with pytest.raises(SatelliteDataUnavailableError):
            specialist.execute(
                request=AnalysisRequest(query="SAR flood mapping through clouds"),
                evidence_collector=EvidenceCollector(),
                provider=failing_provider,
                scene_id="S1_REAL_SCENE_MISSING"
            )
