import logging
import numpy as np
import cv2
from typing import Any
from app.core.exceptions import InvalidROIError

logger = logging.getLogger(__name__)


def crop_roi(img: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    img_h, img_w = img.shape[:2]
    if x < 0 or y < 0 or w <= 0 or h <= 0:
        raise InvalidROIError(f"Invalid ROI params: x={x},y={y},w={w},h={h}")
    if x + w > img_w or y + h > img_h:
        raise InvalidROIError(
            f"ROI ({x},{y},{w},{h}) exceeds image size ({img_w}x{img_h})"
        )
    return img[y:y + h, x:x + w].copy()


def to_grayscale(img: np.ndarray) -> np.ndarray:
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def normalize_contrast(img: np.ndarray) -> np.ndarray:
    gray = to_grayscale(img)
    return cv2.equalizeHist(gray)


def gaussian_blur(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    return cv2.GaussianBlur(img, (k, k), 0)


def median_blur(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    return cv2.medianBlur(img, k)


def threshold_global(img: np.ndarray, thresh_value: int = 127, max_value: int = 255) -> np.ndarray:
    gray = to_grayscale(img)
    _, out = cv2.threshold(gray, thresh_value, max_value, cv2.THRESH_BINARY)
    return out


def threshold_adaptive(img: np.ndarray, block_size: int = 11, C: int = 2) -> np.ndarray:
    gray = to_grayscale(img)
    # OpenCV adaptive threshold requires an odd neighborhood size >= 3.
    bs = max(3, block_size if block_size % 2 == 1 else block_size + 1)
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, bs, C)


def threshold_otsu(img: np.ndarray) -> np.ndarray:
    gray = to_grayscale(img)
    _, out = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return out


def morphology_open(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def morphology_close(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)


def invert(img: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(img)


def resize_upscale(img: np.ndarray, scale_factor: float = 2.0) -> np.ndarray:
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w * scale_factor), int(h * scale_factor)),
                      interpolation=cv2.INTER_CUBIC)


def deskew(img: np.ndarray) -> np.ndarray:
    gray = to_grayscale(img)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    moments = cv2.moments(thresh)
    if abs(moments.get("mu02", 0)) < 1e-2:
        return img
    skew = moments["mu11"] / moments["mu02"]
    angle = np.degrees(np.arctan(skew))
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def run_pipeline(img: np.ndarray, settings: dict[str, Any]) -> np.ndarray:
    """Execute preprocessing pipeline based on settings dict."""
    out = img.copy()
    x = int(settings.get("DEFAULT_ROI_X", 0))
    y = int(settings.get("DEFAULT_ROI_Y", 0))
    w = int(settings.get("DEFAULT_ROI_W", img.shape[1]))
    h = int(settings.get("DEFAULT_ROI_H", img.shape[0]))
    try:
        out = crop_roi(out, x, y, w, h)
    except InvalidROIError as exc:
        logger.warning("Skipping ROI crop: %s", exc)

    out = to_grayscale(out)
    out = deskew(out)

    threshold_mode = settings.get("THRESHOLD_MODE", "OTSU").upper()
    if threshold_mode == "ADAPTIVE":
        out = threshold_adaptive(
            out,
            int(settings.get("THRESHOLD_ADAPTIVE_BLOCK_SIZE", 11)),
            int(settings.get("THRESHOLD_ADAPTIVE_C", 2)),
        )
    elif threshold_mode == "GLOBAL":
        out = threshold_global(out, int(settings.get("THRESHOLD_GLOBAL_VALUE", 127)))
    else:
        out = threshold_otsu(out)

    out = morphology_open(out)
    out = resize_upscale(
        out,
        # TODO: remove lowercase fallback after all clients migrate to UPSCALE_FACTOR.
        float(settings.get("UPSCALE_FACTOR", settings.get("upscale_factor", 2.0))),
    )
    return out
