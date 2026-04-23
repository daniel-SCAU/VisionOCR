import logging
import numpy as np
import cv2
from typing import List

logger = logging.getLogger(__name__)


def sharpness_score(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    lap = cv2.Laplacian(gray.astype(np.float64), cv2.CV_64F)
    return float(lap.var())


def saturation_score(img: np.ndarray) -> float:
    if len(img.shape) == 2:
        return 0.0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return float(hsv[:, :, 1].mean())


def contrast_score(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    return float(gray.std())


def overall_score(img: np.ndarray) -> float:
    sharp = sharpness_score(img)
    contrast = contrast_score(img)
    score = 0.6 * min(sharp / 500.0, 1.0) + 0.4 * min(contrast / 128.0, 1.0)
    return float(score)


def select_best_frame(frames: List[np.ndarray]) -> np.ndarray:
    if not frames:
        raise ValueError("No frames to select from.")
    scores = [overall_score(f) for f in frames]
    best_idx = int(np.argmax(scores))
    logger.debug("Best frame index %d with score %.4f", best_idx, scores[best_idx])
    return frames[best_idx]
