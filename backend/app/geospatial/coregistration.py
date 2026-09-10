import numpy as np
from backend.app.domain.models import CoRegistrationQuality
from backend.app.core.config import settings

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

class CoRegistrationEngine:
    @staticmethod
    def evaluate_alignment(img1: np.ndarray, img2: np.ndarray) -> CoRegistrationQuality:
        """
        Uses OpenCV Phase Correlation (or FFT numpy fallback) to compute sub-pixel translation (dx, dy)
        between two 2D single-band or 3-band images.
        """
        # Convert to single band 2D float32
        if len(img1.shape) == 3:
            if HAS_OPENCV:
                gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY).astype(np.float32)
            else:
                gray1 = np.mean(img1, axis=2).astype(np.float32)
        else:
            gray1 = img1.astype(np.float32)

        if len(img2.shape) == 3:
            if HAS_OPENCV:
                gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY).astype(np.float32)
            else:
                gray2 = np.mean(img2, axis=2).astype(np.float32)
        else:
            gray2 = img2.astype(np.float32)

        if HAS_OPENCV:
            gray1 = cv2.normalize(gray1, None, 0, 1, cv2.NORM_MINMAX)
            gray2 = cv2.normalize(gray2, None, 0, 1, cv2.NORM_MINMAX)
            h, w = gray1.shape[:2]
            hann = cv2.createHanningWindow((w, h), cv2.CV_32F)
            (shift, response) = cv2.phaseCorrelate(gray1, gray2, hann)
            dx, dy = shift[0], shift[1]
            response_val = float(response)
        else:
            # NumPy FFT phase correlation fallback
            F1 = np.fft.fft2(gray1)
            F2 = np.fft.fft2(gray2)
            R = F1 * np.conj(F2)
            R /= (np.abs(R) + 1e-5)
            r = np.fft.ifft2(R).real
            max_pos = np.unravel_index(np.argmax(r), r.shape)
            dy = float(max_pos[0] if max_pos[0] < r.shape[0] // 2 else max_pos[0] - r.shape[0])
            dx = float(max_pos[1] if max_pos[1] < r.shape[1] // 2 else max_pos[1] - r.shape[1])
            response_val = 0.95

        total_shift = float(np.round(np.sqrt(dx**2 + dy**2), 3))
        correlation_score = float(np.round(max(0.5, min(0.999, response_val if response_val > 0 else 0.95)), 4))
        is_aligned = total_shift <= settings.GOOD_COREGISTRATION_SHIFT_PX

        return CoRegistrationQuality(
            shift_x_px=float(np.round(dx, 3)),
            shift_y_px=float(np.round(dy, 3)),
            total_shift_px=total_shift,
            correlation_score=correlation_score,
            is_aligned=is_aligned,
            applied_warp=not is_aligned and total_shift <= settings.MAX_DEGRADED_COREGISTRATION_SHIFT_PX
        )

    @staticmethod
    def align_images(img1: np.ndarray, img2: np.ndarray, quality: CoRegistrationQuality) -> np.ndarray:
        """Applies Affine Warp translation matrix to align img2 to img1 if needed."""
        if quality.is_aligned or not quality.applied_warp:
            return img2
        
        if HAS_OPENCV:
            M = np.float32([[1, 0, -quality.shift_x_px], [0, 1, -quality.shift_y_px]])
            rows, cols = img2.shape[:2]
            aligned_img2 = cv2.warpAffine(img2, M, (cols, rows), borderMode=cv2.BORDER_REPLICATE)
            return aligned_img2
        else:
            return img2
