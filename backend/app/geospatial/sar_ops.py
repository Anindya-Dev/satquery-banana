import numpy as np

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

class SAROps:
    @staticmethod
    def linear_to_db(backscatter: np.ndarray) -> np.ndarray:
        """Convert calibrated linear backscatter from an RTC product to decibels."""
        return 10.0 * np.log10(np.maximum(backscatter.astype(np.float32), 1e-10))
    @staticmethod
    def enhanced_lee_filter(img: np.ndarray, win_size: int = 5, k: float = 1.0, cu: float = 0.52) -> np.ndarray:
        """
        Enhanced Lee Speckle Filter for Sentinel-1 SAR intensity image.
        cu: noise variation coefficient (0.52 for 1-look SAR, lower for multi-look)
        """
        img_f = img.astype(np.float32)
        
        if HAS_OPENCV:
            mean = cv2.blur(img_f, (win_size, win_size))
            mean_sq = cv2.blur(img_f**2, (win_size, win_size))
        else:
            # Pure NumPy sliding window mean fallback
            from scipy.ndimage import uniform_filter
            mean = uniform_filter(img_f, size=win_size)
            mean_sq = uniform_filter(img_f**2, size=win_size)

        variance = mean_sq - mean**2
        variance[variance < 0] = 0

        # Variation coefficient ci = sqrt(var) / mean
        ci = np.sqrt(variance) / (mean + 1e-5)

        # Calculate weight W
        w = np.zeros_like(img_f)
        mask_low = ci <= cu
        mask_high = ci >= (cu * 1.732)
        mask_mid = ~mask_low & ~mask_high

        w[mask_low] = 1.0
        w[mask_high] = 0.0
        if np.any(mask_mid):
            w[mask_mid] = np.exp(-k * (ci[mask_mid] - cu))

        filtered = mean * w + img_f * (1.0 - w)
        return filtered

    @staticmethod
    def calibrate_sigma0_db(dn: np.ndarray, calibration_factor: float = 1.0) -> np.ndarray:
        """Converts raw digital numbers (DN) to Sigma0 backscatter intensity in dB."""
        intensity = (dn.astype(np.float32) * calibration_factor)**2
        intensity[intensity <= 0] = 1e-6
        sigma0_db = 10.0 * np.log10(intensity)
        return sigma0_db
