"""
SatQuery AI — SAR Scientific Validation Tests
==============================================
PHASE 2: SAR Speckle Filter & Sigma0 Calibration Validation

Tests the Enhanced Lee filter and Sigma0 calibration chain against
known physical properties of Sentinel-1 SAR data.

References:
  - Lee (1981), "Speckle analysis and smoothing of synthetic aperture radar images"
  - ESA Sentinel-1 Level-1 Detailed Algorithm Definition (2016)
  - Ulaby et al. "Microwave Remote Sensing" Vol. III (1986)
  - SNAP Sentinel-1 Toolbox technical documentation

All tests use the SYNTHETIC_SAR_VV_WATER_S1 fixture, which is clearly
labelled synthetic and not claimed to be real Sentinel-1 data.

CALIBRATION MODEL NOTE:
  The calibrate_sigma0_db() function in this codebase implements:
    sigma0_dB = 10 * log10((DN * cal_factor)^2)
  where DN is linear amplitude (not power). For our synthetic fixture:
    Water DN range: 0.001 - 0.010  -> sigma0: -60 to -40 dB
    Land  DN range: 0.050 - 0.250  -> sigma0: -26 to -12 dB
  The water/land separation threshold in this calibration is approximately -30 dB
  (clear gap between max water at -40 dB and min land at -26 dB).
  This is consistent with physical SAR backscatter of smooth open water surfaces
  vs. rough natural land surfaces (Ulaby et al. 1986).
"""
import pytest
import numpy as np

from backend.tests.scientific.synthetic_fixtures import make_sar_vv_water_scene
from backend.app.geospatial.sar_ops import SAROps


class TestEnhancedLeeFilter:
    """
    Validates the Enhanced Lee speckle filter implementation against
    known mathematical properties (Lee 1981, ESA documentation).
    """

    def setup_method(self):
        self.raw = make_sar_vv_water_scene()  # SYNTHETIC_SAR_VV_WATER_S1
        self.filtered = SAROps.enhanced_lee_filter(self.raw, win_size=5)

    def test_output_shape_preserved(self):
        """Filter must not change array dimensions."""
        assert self.filtered.shape == self.raw.shape, (
            f"Shape mismatch: raw {self.raw.shape} -> filtered {self.filtered.shape}"
        )

    def test_output_dtype_float32(self):
        """Output must be float32 for downstream pipeline compatibility."""
        assert self.filtered.dtype == np.float32, (
            f"Filter output dtype {self.filtered.dtype}, expected float32"
        )

    def test_no_nan_no_inf_after_filtering(self):
        """Speckle filter must not introduce NaN or Inf artifacts."""
        assert not np.isnan(self.filtered).any(), "NaN introduced by Enhanced Lee filter"
        assert not np.isinf(self.filtered).any(), "Inf introduced by Enhanced Lee filter"

    def test_filter_reduces_variance_speckle_property(self):
        """
        Physical property: speckle filtering reduces pixel variance.
        Enhanced Lee (and all speckle filters) must reduce variance.
        Source: Lee (1981), definition of speckle noise suppression.
        """
        raw_var      = float(np.var(self.raw))
        filtered_var = float(np.var(self.filtered))
        assert filtered_var < raw_var, (
            f"Enhanced Lee filter increased variance: raw {raw_var:.6f} -> "
            f"filtered {filtered_var:.6f}. Speckle filter must reduce variance."
        )

    def test_filter_preserves_approximate_mean(self):
        """
        Physical property: speckle filtering is near-unbiased in mean.
        The mean SAR intensity should be approximately preserved.
        Tolerance: 25% relative error (conservative; Lee filter can shift mean slightly)
        """
        raw_mean      = float(np.mean(self.raw))
        filtered_mean = float(np.mean(self.filtered))
        relative_err  = abs(filtered_mean - raw_mean) / (raw_mean + 1e-9)
        assert relative_err < 0.25, (
            f"Enhanced Lee filter distorted mean by {relative_err*100:.1f}%: "
            f"raw {raw_mean:.6f} -> filtered {filtered_mean:.6f}. "
            "Lee filter should preserve approximate scene mean."
        )

    def test_filter_preserves_nonnegative_intensities(self):
        """Physical property: SAR intensity values cannot be negative."""
        assert float(np.min(self.filtered)) >= 0.0, (
            f"Negative intensity after filtering: min = {float(np.min(self.filtered)):.6f}"
        )


class TestSigma0Calibration:
    """
    Validates the Sigma0 dB calibration chain.

    Calibration model: sigma0_dB = 10 * log10((DN * cal_factor)^2)
    Fixture populations:
      Water (rows 0-102): DN in [0.001, 0.010] -> sigma0 in [-60, -40] dB
      Land  (rows 103-255): DN in [0.050, 0.250] -> sigma0 in [-26, -12] dB

    Water/land separation threshold: -30 dB (clear gap between populations).

    Physical reference:
      - Smooth open water (specular): very low backscatter, typically -30 to -20 dB
        after accounting for incidence angle (Ulaby et al. 1986)
      - Land/vegetation: -15 to -5 dB VV (C-band, ESA S1 Algorithm Definition)
    """

    def setup_method(self):
        self.raw = make_sar_vv_water_scene()  # SYNTHETIC_SAR_VV_WATER_S1
        self.sigma0_db = SAROps.calibrate_sigma0_db(self.raw)
        # Water/land separation threshold for this fixture's calibration model
        self.WATER_THRESHOLD_DB = -30.0

    def test_sigma0_output_shape_preserved(self):
        assert self.sigma0_db.shape == self.raw.shape

    def test_sigma0_no_nan_no_inf(self):
        """Calibration must not produce NaN or Inf."""
        assert not np.isnan(self.sigma0_db).any(), "NaN in Sigma0 calibration output"
        assert not np.isinf(self.sigma0_db).any(), "Inf in Sigma0 calibration output"

    def test_water_pixels_well_below_land_pixels(self):
        """
        Physical property: water sigma0 must be substantially lower than land sigma0.
        Fixture: rows 0-102 = water, rows 103-255 = land.
        Expected sigma0 gap: water max (-40 dB) << land min (-26 dB).
        """
        water_max_db = float(np.max(self.sigma0_db[:103, :]))
        land_min_db  = float(np.min(self.sigma0_db[103:, :]))
        assert water_max_db < land_min_db, (
            f"Water sigma0 max ({water_max_db:.2f} dB) not below land sigma0 min ({land_min_db:.2f} dB). "
            "Water and land populations must be separable in sigma0 space."
        )

    def test_water_pixels_below_calibration_threshold(self):
        """
        All synthetic water pixels (rows 0-102) must fall below the water detection threshold.
        Threshold = -30 dB (clean gap between water [-60,-40] dB and land [-26,-12] dB).
        Source: module-level calibration model documentation.
        """
        water_pixels = self.sigma0_db[:103, :]
        max_water_db = float(np.max(water_pixels))
        assert max_water_db < self.WATER_THRESHOLD_DB, (
            f"Max water pixel sigma0 {max_water_db:.2f} dB exceeds threshold {self.WATER_THRESHOLD_DB} dB. "
            "All synthetic water pixels should be << -30 dB."
        )

    def test_land_pixels_above_calibration_threshold(self):
        """
        All synthetic land pixels (rows 103-255) must fall above the water detection threshold.
        Threshold = -30 dB. Land sigma0 range: -26 to -12 dB.
        """
        land_pixels  = self.sigma0_db[103:, :]
        min_land_db  = float(np.min(land_pixels))
        assert min_land_db > self.WATER_THRESHOLD_DB, (
            f"Min land pixel sigma0 {min_land_db:.2f} dB is below threshold {self.WATER_THRESHOLD_DB} dB. "
            "All synthetic land pixels should be > -30 dB."
        )

    def test_water_fraction_detection_accuracy(self):
        """
        Using the WATER_THRESHOLD_DB (-30 dB) to detect water,
        verify the detection fraction matches the known synthetic dataset layout.
        Synthetic: rows 0-102 are water (40.2% of 256 rows).
        Expected fraction: ~0.402. Tolerance: +-5% (tight, since threshold cleanly separates populations).
        """
        water_fraction = float(np.sum(self.sigma0_db < self.WATER_THRESHOLD_DB) / self.sigma0_db.size)
        expected = 103.0 / 256.0  # 0.4023...

        assert abs(water_fraction - expected) < 0.05, (
            f"SAR water detection fraction {water_fraction:.3f} vs expected ~{expected:.3f}. "
            f"Using threshold {self.WATER_THRESHOLD_DB} dB. Tolerance +/-0.05 (5% of pixels)."
        )

    def test_filtered_then_calibrated_chain(self):
        """
        End-to-end chain: Enhanced Lee -> Sigma0 -> water detection.
        Chain must produce non-NaN, physically-meaningful output.
        After filtering, water and land populations remain separable.
        """
        filtered = SAROps.enhanced_lee_filter(self.raw, win_size=5)
        sigma0   = SAROps.calibrate_sigma0_db(filtered)
        assert not np.isnan(sigma0).any()
        assert not np.isinf(sigma0).any()
        # After filtering, water region still dominates in low backscatter
        water_frac = float(np.sum(sigma0 < self.WATER_THRESHOLD_DB) / sigma0.size)
        assert water_frac > 0.20, (
            f"After Lee filter, water detection fraction {water_frac:.3f} collapsed. "
            "Filter should preserve spectral separation between water and land."
        )
