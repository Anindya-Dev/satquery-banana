import numpy as np
from typing import Dict, Any, Tuple

class RasterOps:
    @staticmethod
    def _sanitize_and_compute(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        a_f = np.nan_to_num(a.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        b_f = np.nan_to_num(b.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        denom = a_f + b_f
        denom = np.where(np.abs(denom) < 1e-6, 1e-6, denom)
        res = (a_f - b_f) / denom
        return np.clip(np.nan_to_num(res, nan=0.0, posinf=1.0, neginf=-1.0), -1.0, 1.0)

    @staticmethod
    def calculate_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Normalized Difference Vegetation Index: (NIR - Red) / (NIR + Red)"""
        return RasterOps._sanitize_and_compute(nir, red)

    @staticmethod
    def calculate_ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """Normalized Difference Water Index: (Green - NIR) / (Green + NIR)"""
        return RasterOps._sanitize_and_compute(green, nir)

    @staticmethod
    def calculate_mndwi(green: np.ndarray, swir: np.ndarray) -> np.ndarray:
        """Modified Normalized Difference Water Index: (Green - SWIR) / (Green + SWIR)"""
        return RasterOps._sanitize_and_compute(green, swir)

    @staticmethod
    def calculate_ndbi(swir: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """Normalized Difference Built-up Index: (SWIR - NIR) / (SWIR + NIR)"""
        return RasterOps._sanitize_and_compute(swir, nir)

    @staticmethod
    def calculate_nbr(nir: np.ndarray, swir2: np.ndarray) -> np.ndarray:
        """Normalized Burn Ratio: (NIR - SWIR2) / (NIR + SWIR2)"""
        return RasterOps._sanitize_and_compute(nir, swir2)

    @staticmethod
    def get_index_stats(index_array: np.ndarray) -> Dict[str, float]:
        clean_arr = index_array[~np.isnan(index_array) & ~np.isinf(index_array)]
        if clean_arr.size == 0:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "std": 0.0}
        return {
            "mean": float(np.round(np.mean(clean_arr), 4)),
            "min": float(np.round(np.min(clean_arr), 4)),
            "max": float(np.round(np.max(clean_arr), 4)),
            "std": float(np.round(np.std(clean_arr), 4))
        }

    @staticmethod
    def compute_bitemporal_diff(t1_img: np.ndarray, t2_img: np.ndarray, threshold: float = 0.2) -> Tuple[np.ndarray, float, float]:
        """Calculates absolute pixel difference and binary change mask."""
        diff = np.abs(t2_img.astype(np.float32) - t1_img.astype(np.float32))
        change_mask = (diff > threshold).astype(np.uint8)
        changed_pixels = int(np.sum(change_mask))
        total_pixels = change_mask.size
        pct_changed = float(np.round((changed_pixels / total_pixels) * 100.0, 2))
        return diff, change_mask, pct_changed
