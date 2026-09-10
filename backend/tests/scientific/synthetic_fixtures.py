"""
SatQuery AI — Scientific Synthetic Fixture Library
====================================================
IMPORTANT: These are SYNTHETIC datasets, NOT real satellite pixels.
They are physically-realistic (values sampled from published Sentinel-2 L2A
surface reflectance statistics) and used exclusively for deterministic
algorithm validation.

Sources for reflectance ranges:
  - Sentinel-2 L2A Technical Guide ESA (2023)
  - Drusch et al. (2012) "Sentinel-2: ESA's Optical High-Resolution Mission"
  - Tucker (1979) "Red and photographic infrared linear combinations for monitoring vegetation"
  - McFeeters (1996) "The use of NDWI to delineate open water features"
  - Xu (2006) "Modification of NDWI to enhance open water features"

All arrays are seeded for strict reproducibility.
"""
import numpy as np
from typing import Dict

# ─── Global RNG seed for all fixtures ────────────────────────────────────────
FIXTURE_SEED = 20240901  # YYYY-MM-DD fixed seed


def _rng() -> np.random.Generator:
    return np.random.default_rng(seed=FIXTURE_SEED)


# ─── Sentinel-2 L2A Surface Reflectance Reference Ranges ─────────────────────
# Reflectance values are in [0, 1] (L2A BOA, divided by 10000 from integer DN)
#
# Source: Sentinel-2 L2A spectral library / typical land-cover statistics
# Band  | Water  | Vegetation | Urban/Soil | Forest
# B2 (Blue)  0.02-0.06 | 0.02-0.04 | 0.08-0.18 | 0.02-0.04
# B3 (Green) 0.04-0.12 | 0.04-0.08 | 0.10-0.22 | 0.03-0.06
# B4 (Red)   0.02-0.06 | 0.03-0.06 | 0.12-0.25 | 0.02-0.04
# B8 (NIR)   0.02-0.06 | 0.35-0.65 | 0.18-0.38 | 0.40-0.70
# B11 (SWIR) 0.02-0.04 | 0.05-0.20 | 0.15-0.35 | 0.04-0.12

SHAPE = (256, 256)


def make_dense_vegetation_scene() -> Dict[str, np.ndarray]:
    """
    Synthetic Sentinel-2 L2A scene: dense tropical/temperate vegetation.
    Expected NDVI: ~0.55 - 0.75 (healthy canopy)
    Expected NDWI: negative (vegetation, not water)
    Data label: SYNTHETIC_DENSE_VEGETATION_S2L2A
    """
    rng = _rng()
    return {
        "scene_label": "SYNTHETIC_DENSE_VEGETATION_S2L2A",
        "B3": rng.uniform(0.04, 0.08, SHAPE).astype(np.float32),  # Green
        "B4": rng.uniform(0.03, 0.06, SHAPE).astype(np.float32),  # Red
        "B8": rng.uniform(0.40, 0.65, SHAPE).astype(np.float32),  # NIR
        "B11": rng.uniform(0.05, 0.12, SHAPE).astype(np.float32), # SWIR
    }


def make_open_water_scene() -> Dict[str, np.ndarray]:
    """
    Synthetic Sentinel-2 L2A scene: open water body (clear).
    Expected NDWI: ~0.20 - 0.45 (positive → water)
    Expected NDVI: ~-0.25 (near-zero NIR, slightly more green)
    Data label: SYNTHETIC_OPEN_WATER_S2L2A
    """
    rng = _rng()
    return {
        "scene_label": "SYNTHETIC_OPEN_WATER_S2L2A",
        "B3": rng.uniform(0.06, 0.12, SHAPE).astype(np.float32),  # Green (brighter)
        "B4": rng.uniform(0.02, 0.05, SHAPE).astype(np.float32),  # Red (low)
        "B8": rng.uniform(0.02, 0.05, SHAPE).astype(np.float32),  # NIR (very low)
        "B11": rng.uniform(0.01, 0.03, SHAPE).astype(np.float32), # SWIR (very low)
    }


def make_urban_impervious_scene() -> Dict[str, np.ndarray]:
    """
    Synthetic Sentinel-2 L2A scene: urban / impervious surfaces.
    Expected NDBI: positive (built-up > vegetation)
    Expected NDVI: low (~0.05 - 0.15)
    Data label: SYNTHETIC_URBAN_IMPERVIOUS_S2L2A
    """
    rng = _rng()
    return {
        "scene_label": "SYNTHETIC_URBAN_IMPERVIOUS_S2L2A",
        "B3": rng.uniform(0.12, 0.22, SHAPE).astype(np.float32),  # Green (higher)
        "B4": rng.uniform(0.15, 0.25, SHAPE).astype(np.float32),  # Red (higher)
        "B8": rng.uniform(0.18, 0.32, SHAPE).astype(np.float32),  # NIR (medium)
        "B11": rng.uniform(0.20, 0.38, SHAPE).astype(np.float32), # SWIR (high → built-up)
    }


def make_burned_area_scene() -> Dict[str, np.ndarray]:
    """
    Synthetic Sentinel-2 L2A scene: post-fire burned area.
    Expected NBR: strongly negative (low NIR, high SWIR2)
    Expected NDVI: near zero or negative
    Data label: SYNTHETIC_BURNED_AREA_S2L2A
    """
    rng = _rng()
    return {
        "scene_label": "SYNTHETIC_BURNED_AREA_S2L2A",
        "B3": rng.uniform(0.05, 0.10, SHAPE).astype(np.float32),  # Green (low)
        "B4": rng.uniform(0.05, 0.12, SHAPE).astype(np.float32),  # Red (low-medium)
        "B8": rng.uniform(0.06, 0.12, SHAPE).astype(np.float32),  # NIR (low: burned)
        "B11": rng.uniform(0.22, 0.42, SHAPE).astype(np.float32), # SWIR (high: char)
    }


def make_inundation_before_after_pair() -> Dict[str, Dict[str, np.ndarray]]:
    """
    Synthetic bi-temporal pair simulating Kolkata-style monsoon inundation.
    T1: Dry pre-monsoon (dominant vegetation + some water)
    T2: Post-monsoon flood (dominant water + reduced vegetation)
    Expected NDWI delta (T2 - T1): significantly positive
    Data label: SYNTHETIC_INUNDATION_CHANGE_PAIR_S2L2A
    """
    rng = _rng()
    # T1: Mostly vegetation, small water
    t1_green = rng.uniform(0.04, 0.08, SHAPE).astype(np.float32)
    t1_nir = rng.uniform(0.38, 0.60, SHAPE).astype(np.float32)
    # T2: Large fraction converted to water (force lower NIR, higher green)
    t2_green = rng.uniform(0.08, 0.14, SHAPE).astype(np.float32)
    t2_nir = rng.uniform(0.04, 0.10, SHAPE).astype(np.float32)

    return {
        "label": "SYNTHETIC_INUNDATION_CHANGE_PAIR_S2L2A",
        "T1": {"B3": t1_green, "B8": t1_nir},
        "T2": {"B3": t2_green, "B8": t2_nir},
    }


def make_sar_vv_water_scene() -> np.ndarray:
    """
    Synthetic Sentinel-1 SAR VV intensity scene (linear power, not dB).
    Water pixels: very low backscatter (specular reflection: 0.001–0.01 linear)
    Land pixels: moderate backscatter (0.05–0.25 linear)
    Expected sigma0 < -15 dB for water fraction.
    Data label: SYNTHETIC_SAR_VV_WATER_S1
    """
    rng = _rng()
    arr = np.empty(SHAPE, dtype=np.float32)
    # 40% water pixels (rows 0..102)
    arr[:103, :] = rng.uniform(0.001, 0.010, (103, SHAPE[1]))
    # 60% land pixels (rows 103..255)
    arr[103:, :] = rng.uniform(0.050, 0.250, (153, SHAPE[1]))
    return arr


def make_perfectly_aligned_pair() -> tuple:
    """
    Two identical images → expected total_shift_px ≈ 0.0 (GOOD tier).
    """
    rng = _rng()
    img = (rng.uniform(0, 1, (256, 256)) * 255).astype(np.uint8)
    return img, img.copy()


def make_degraded_alignment_pair() -> tuple:
    """
    Image pair with 4-pixel translation → DEGRADED tier (3 < shift ≤ 6).
    Applied warp should be True.
    """
    rng = _rng()
    img1 = (rng.uniform(0, 1, (256, 256)) * 255).astype(np.uint8)
    # Translate img2 by exactly 4 pixels (within DEGRADED range)
    img2 = np.roll(img1, shift=4, axis=1)
    return img1, img2


def make_unusable_alignment_pair() -> tuple:
    """
    Image pair with 8-pixel translation → UNUSABLE tier (shift > 6).
    Should trigger refusal.
    """
    rng = _rng()
    img1 = (rng.uniform(0, 1, (256, 256)) * 255).astype(np.uint8)
    img2 = np.roll(img1, shift=8, axis=1)
    return img1, img2
