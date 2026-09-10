"""
SatQuery AI — Scientific Spectral Index Validation Tests
=========================================================
PHASE 1: Index Accuracy Regression Suite

Tests deterministic correctness of all five spectral indices
against physically-realistic Sentinel-2 L2A synthetic scenes.

Validation criteria are derived from published literature:
  - NDVI vegetation: > 0.4 (healthy dense canopy, Tucker 1979)
  - NDWI water: > 0.0 (positive for open water, McFeeters 1996)
  - NDBI urban: > 0.0 (positive for impervious, Zha et al. 2003)
  - NBR burned: < 0.0 (negative post-fire, Key & Benson 2006)
  - MNDWI water: > NDWI (better water separation, Xu 2006)

NO FABRICATED VALUES. All assertions are bounded by physical expectation,
not hardcoded magic numbers.
"""
import pytest
import numpy as np

from backend.tests.scientific.synthetic_fixtures import (
    make_dense_vegetation_scene,
    make_open_water_scene,
    make_urban_impervious_scene,
    make_burned_area_scene,
    make_inundation_before_after_pair,
)
from backend.app.geospatial.raster_ops import RasterOps


# ─────────────────────────────────────────────────────────────────────────────
# NDVI — Dense Vegetation Scene
# ─────────────────────────────────────────────────────────────────────────────
class TestNDVIVegetationScene:
    """NDVI should be strongly positive for dense vegetation."""

    def setup_method(self):
        self.scene = make_dense_vegetation_scene()
        self.ndvi = RasterOps.calculate_ndvi(self.scene["B8"], self.scene["B4"])
        self.stats = RasterOps.get_index_stats(self.ndvi)

    def test_ndvi_range_valid(self):
        """All NDVI values must lie in [-1, 1]."""
        assert float(self.stats["min"]) >= -1.0, "NDVI below -1.0 detected"
        assert float(self.stats["max"]) <= 1.0,  "NDVI above 1.0 detected"

    def test_ndvi_mean_indicates_vegetation(self):
        """Dense vegetation: published mean NDVI >= 0.40 (Tucker 1979)."""
        assert self.stats["mean"] >= 0.40, (
            f"NDVI mean {self.stats['mean']:.4f} < 0.40 for dense vegetation scene. "
            "Expected healthy canopy reflectance based on published S2 L2A statistics."
        )

    def test_ndvi_no_nan_no_inf(self):
        """Index must never produce NaN or Inf."""
        assert not np.isnan(self.ndvi).any(), "NaN in NDVI output"
        assert not np.isinf(self.ndvi).any(), "Inf in NDVI output"

    def test_ndvi_higher_than_water_scene(self):
        """Vegetation NDVI must exceed water NDVI (negative)."""
        water_scene = make_open_water_scene()
        water_ndvi = RasterOps.calculate_ndvi(water_scene["B8"], water_scene["B4"])
        water_stats = RasterOps.get_index_stats(water_ndvi)
        assert self.stats["mean"] > water_stats["mean"], (
            "Vegetation NDVI must exceed water NDVI"
        )


# ─────────────────────────────────────────────────────────────────────────────
# NDWI — Open Water Scene
# ─────────────────────────────────────────────────────────────────────────────
class TestNDWIWaterScene:
    """NDWI should be positive for open water bodies."""

    def setup_method(self):
        self.scene = make_open_water_scene()
        self.ndwi = RasterOps.calculate_ndwi(self.scene["B3"], self.scene["B8"])
        self.stats = RasterOps.get_index_stats(self.ndwi)

    def test_ndwi_range_valid(self):
        assert float(self.stats["min"]) >= -1.0
        assert float(self.stats["max"]) <= 1.0

    def test_ndwi_positive_for_water(self):
        """Open water: NDWI > 0.0 (McFeeters 1996). Typical range 0.20-0.45."""
        assert self.stats["mean"] > 0.0, (
            f"NDWI mean {self.stats['mean']:.4f} is non-positive for water scene. "
            "McFeeters (1996): NDWI > 0.0 for open water."
        )

    def test_ndwi_lower_for_vegetation(self):
        """Vegetation scene NDWI should be negative (green < NIR for plants)."""
        veg_scene = make_dense_vegetation_scene()
        veg_ndwi = RasterOps.calculate_ndwi(veg_scene["B3"], veg_scene["B8"])
        veg_stats = RasterOps.get_index_stats(veg_ndwi)
        assert veg_stats["mean"] < self.stats["mean"], (
            "Water NDWI must exceed vegetation NDWI"
        )

    def test_ndwi_no_nan_no_inf(self):
        assert not np.isnan(self.ndwi).any()
        assert not np.isinf(self.ndwi).any()


# ─────────────────────────────────────────────────────────────────────────────
# MNDWI — Open Water Scene (Modified)
# ─────────────────────────────────────────────────────────────────────────────
class TestMNDWIWaterScene:
    """MNDWI should outperform NDWI for separating water from built-up."""

    def setup_method(self):
        self.scene = make_open_water_scene()
        self.mndwi = RasterOps.calculate_mndwi(self.scene["B3"], self.scene["B11"])
        self.ndwi  = RasterOps.calculate_ndwi(self.scene["B3"], self.scene["B8"])
        self.mndwi_stats = RasterOps.get_index_stats(self.mndwi)
        self.ndwi_stats  = RasterOps.get_index_stats(self.ndwi)

    def test_mndwi_positive_for_water(self):
        """Xu (2006): MNDWI > 0 for open water, with better contrast than NDWI."""
        assert self.mndwi_stats["mean"] > 0.0, (
            f"MNDWI mean {self.mndwi_stats['mean']:.4f} non-positive for water scene."
        )

    def test_mndwi_greater_than_ndwi_for_water(self):
        """Xu (2006): MNDWI provides stronger water signal than NDWI (SWIR lower than NIR for water)."""
        assert self.mndwi_stats["mean"] >= self.ndwi_stats["mean"], (
            f"MNDWI mean {self.mndwi_stats['mean']:.4f} not >= NDWI mean {self.ndwi_stats['mean']:.4f}. "
            "MNDWI should have equal or stronger water signal (Xu 2006)."
        )

    def test_mndwi_no_nan_no_inf(self):
        assert not np.isnan(self.mndwi).any()
        assert not np.isinf(self.mndwi).any()


# ─────────────────────────────────────────────────────────────────────────────
# NDBI — Urban / Impervious Scene
# ─────────────────────────────────────────────────────────────────────────────
class TestNDBIUrbanScene:
    """NDBI should be positive for impervious/built-up surfaces."""

    def setup_method(self):
        self.scene = make_urban_impervious_scene()
        self.ndbi = RasterOps.calculate_ndbi(self.scene["B11"], self.scene["B8"])
        self.stats = RasterOps.get_index_stats(self.ndbi)

    def test_ndbi_range_valid(self):
        assert float(self.stats["min"]) >= -1.0
        assert float(self.stats["max"]) <= 1.0

    def test_ndbi_positive_for_urban(self):
        """Zha et al. (2003): NDBI > 0 for built-up surfaces (SWIR > NIR)."""
        assert self.stats["mean"] > 0.0, (
            f"NDBI mean {self.stats['mean']:.4f} not positive for urban scene. "
            "Zha et al. (2003): SWIR > NIR for impervious surfaces -> NDBI > 0."
        )

    def test_ndbi_lower_for_vegetation(self):
        """Urban NDBI must exceed vegetation NDBI (vegetation has high NIR)."""
        veg_scene = make_dense_vegetation_scene()
        veg_ndbi = RasterOps.calculate_ndbi(veg_scene["B11"], veg_scene["B8"])
        veg_stats = RasterOps.get_index_stats(veg_ndbi)
        assert self.stats["mean"] > veg_stats["mean"], (
            "Urban NDBI must exceed vegetation NDBI"
        )

    def test_ndbi_no_nan_no_inf(self):
        assert not np.isnan(self.ndbi).any()
        assert not np.isinf(self.ndbi).any()


# ─────────────────────────────────────────────────────────────────────────────
# NBR — Burned Area Scene
# ─────────────────────────────────────────────────────────────────────────────
class TestNBRBurnedAreaScene:
    """NBR should be strongly negative for post-fire burned areas."""

    def setup_method(self):
        self.scene = make_burned_area_scene()
        self.nbr = RasterOps.calculate_nbr(self.scene["B8"], self.scene["B11"])
        self.stats = RasterOps.get_index_stats(self.nbr)

    def test_nbr_range_valid(self):
        assert float(self.stats["min"]) >= -1.0
        assert float(self.stats["max"]) <= 1.0

    def test_nbr_negative_for_burned_area(self):
        """Key & Benson (2006): NBR < 0 for burned area (low NIR, high SWIR2)."""
        assert self.stats["mean"] < 0.0, (
            f"NBR mean {self.stats['mean']:.4f} not negative for burned area. "
            "Key & Benson (2006): low NIR + high SWIR2 -> NBR < 0 post-fire."
        )

    def test_nbr_much_lower_than_vegetation(self):
        """Burned NBR must be substantially below healthy vegetation NBR."""
        veg_scene = make_dense_vegetation_scene()
        veg_nbr = RasterOps.calculate_nbr(veg_scene["B8"], veg_scene["B11"])
        veg_stats = RasterOps.get_index_stats(veg_nbr)
        assert self.stats["mean"] < veg_stats["mean"], (
            "Burned area NBR must be below healthy vegetation NBR"
        )

    def test_nbr_no_nan_no_inf(self):
        assert not np.isnan(self.nbr).any()
        assert not np.isinf(self.nbr).any()


# ─────────────────────────────────────────────────────────────────────────────
# Bitemporal Change Detection — Inundation Pair
# ─────────────────────────────────────────────────────────────────────────────
class TestBitemporalInundationChangeDetection:
    """
    Tests bi-temporal NDWI delta correctness for monsoon inundation scenario.
    NDWI must increase significantly from T1 (dry) to T2 (flood).
    """

    def setup_method(self):
        self.pair = make_inundation_before_after_pair()
        t1 = self.pair["T1"]
        t2 = self.pair["T2"]
        self.t1_ndwi = RasterOps.calculate_ndwi(t1["B3"], t1["B8"])
        self.t2_ndwi = RasterOps.calculate_ndwi(t2["B3"], t2["B8"])
        self.t1_stats = RasterOps.get_index_stats(self.t1_ndwi)
        self.t2_stats = RasterOps.get_index_stats(self.t2_ndwi)
        _, self.change_mask, self.pct_changed = RasterOps.compute_bitemporal_diff(
            self.t1_ndwi, self.t2_ndwi, threshold=0.10
        )

    def test_t1_ndwi_negative_dry_season(self):
        """T1 (pre-monsoon): NDWI should be negative (vegetation dominant)."""
        assert self.t1_stats["mean"] < 0.0, (
            f"T1 NDWI mean {self.t1_stats['mean']:.4f} should be negative for dry-season scene."
        )

    def test_t2_ndwi_positive_flood(self):
        """T2 (post-monsoon): NDWI should be positive (water dominant)."""
        assert self.t2_stats["mean"] > 0.0, (
            f"T2 NDWI mean {self.t2_stats['mean']:.4f} should be positive for flood scene."
        )

    def test_ndwi_delta_positive_inundation(self):
        """NDWI must increase from T1 to T2 for genuine inundation."""
        delta = self.t2_stats["mean"] - self.t1_stats["mean"]
        assert delta > 0.0, (
            f"NDWI delta {delta:.4f} is not positive. "
            "Inundation should increase NDWI from T1->T2."
        )

    def test_change_mask_captures_inundation(self):
        """A significant fraction of pixels must show change (realistic flood)."""
        assert self.pct_changed > 0.0, "Change detection percent must be > 0"
        assert self.pct_changed > 1.0, (
            f"Only {self.pct_changed}% change detected; expected meaningful inundation change."
        )

    def test_bitemporal_no_nan_no_inf(self):
        assert not np.isnan(self.t1_ndwi).any()
        assert not np.isnan(self.t2_ndwi).any()
        assert not np.isinf(self.t1_ndwi).any()
        assert not np.isinf(self.t2_ndwi).any()


# ─────────────────────────────────────────────────────────────────────────────
# Cross-Scene Index Ordering: Physical Invariants
# ─────────────────────────────────────────────────────────────────────────────
class TestCrossScenePhysicalInvariants:
    """
    Tests that spectral indices preserve known physical ordering relationships
    across land-cover types (scene type x index invariants).
    These are non-negotiable physical laws, not implementation choices.
    """

    def test_ndvi_ordering_invariant(self):
        """
        Known physical ordering: Vegetation NDVI > Urban NDVI > Water NDVI
        Source: Copernicus Land Cover classification statistics
        """
        veg   = make_dense_vegetation_scene()
        urban = make_urban_impervious_scene()
        water = make_open_water_scene()

        ndvi_veg   = RasterOps.get_index_stats(RasterOps.calculate_ndvi(veg["B8"],   veg["B4"]))[  "mean"]
        ndvi_urban = RasterOps.get_index_stats(RasterOps.calculate_ndvi(urban["B8"], urban["B4"]))["mean"]
        ndvi_water = RasterOps.get_index_stats(RasterOps.calculate_ndvi(water["B8"], water["B4"]))["mean"]

        assert ndvi_veg > ndvi_urban, (
            f"Vegetation NDVI ({ndvi_veg:.3f}) must exceed Urban NDVI ({ndvi_urban:.3f})"
        )
        assert ndvi_urban > ndvi_water, (
            f"Urban NDVI ({ndvi_urban:.3f}) must exceed Water NDVI ({ndvi_water:.3f})"
        )

    def test_ndwi_ordering_invariant(self):
        """
        Known physical ordering: Water NDWI > Urban NDWI > Vegetation NDWI

        Physical basis (Sentinel-2 L2A surface reflectance):
          - Water: high Green (0.06-0.12), very low NIR (0.02-0.05) -> NDWI strongly positive
          - Urban: moderate Green (0.12-0.22), moderate NIR (0.18-0.32) -> NDWI slightly negative
          - Dense vegetation: low Green (0.04-0.08), very high NIR (0.40-0.65) -> NDWI very negative

        Dense vegetation's very high NIR numerically dominates, driving NDWI far negative (~-0.79).
        Urban NIR is moderate, so NDWI is only slightly negative (~-0.19).
        Correct ordering: Water > Urban > Vegetation.
        Source: McFeeters (1996), Sentinel-2 L2A spectral response library.
        """
        veg   = make_dense_vegetation_scene()
        urban = make_urban_impervious_scene()
        water = make_open_water_scene()

        ndwi_veg   = RasterOps.get_index_stats(RasterOps.calculate_ndwi(veg["B3"],   veg["B8"]))[  "mean"]
        ndwi_urban = RasterOps.get_index_stats(RasterOps.calculate_ndwi(urban["B3"], urban["B8"]))["mean"]
        ndwi_water = RasterOps.get_index_stats(RasterOps.calculate_ndwi(water["B3"], water["B8"]))["mean"]

        assert ndwi_water > ndwi_urban, (
            f"Water NDWI ({ndwi_water:.3f}) must exceed Urban NDWI ({ndwi_urban:.3f})"
        )
        assert ndwi_urban > ndwi_veg, (
            f"Urban NDWI ({ndwi_urban:.3f}) must exceed Vegetation NDWI ({ndwi_veg:.3f}). "
            "Dense vegetation's high NIR (0.40-0.65) drives NDWI very negative."
        )

    def test_ndbi_ordering_invariant(self):
        """
        Known physical ordering: Urban NDBI > Vegetation NDBI (urban has high SWIR)
        """
        veg   = make_dense_vegetation_scene()
        urban = make_urban_impervious_scene()

        ndbi_veg   = RasterOps.get_index_stats(RasterOps.calculate_ndbi(veg["B11"],   veg["B8"]))[  "mean"]
        ndbi_urban = RasterOps.get_index_stats(RasterOps.calculate_ndbi(urban["B11"], urban["B8"]))["mean"]

        assert ndbi_urban > ndbi_veg, (
            f"Urban NDBI ({ndbi_urban:.3f}) must exceed Vegetation NDBI ({ndbi_veg:.3f})"
        )
