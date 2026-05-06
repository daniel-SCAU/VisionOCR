import pytest
import numpy as np
import cv2
from app.services.preprocess import (
    crop_roi, to_grayscale, normalize_contrast, gaussian_blur, median_blur,
    threshold_global, threshold_adaptive, threshold_otsu, morphology_open,
    morphology_close, invert, resize_upscale, deskew, run_pipeline,
)
from app.core.exceptions import InvalidROIError


def make_gray(h=100, w=100):
    return np.random.randint(0, 256, (h, w), dtype=np.uint8)


def make_bgr(h=100, w=100):
    return np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)


def test_crop_roi_valid():
    img = make_bgr(200, 200)
    out = crop_roi(img, 10, 10, 50, 50)
    assert out.shape == (50, 50, 3)


def test_crop_roi_invalid_size():
    img = make_bgr(100, 100)
    with pytest.raises(InvalidROIError):
        crop_roi(img, 0, 0, 200, 200)


def test_crop_roi_negative():
    img = make_bgr(100, 100)
    with pytest.raises(InvalidROIError):
        crop_roi(img, -1, 0, 50, 50)


def test_crop_roi_zero_w():
    img = make_bgr(100, 100)
    with pytest.raises(InvalidROIError):
        crop_roi(img, 0, 0, 0, 50)


def test_to_grayscale_bgr():
    img = make_bgr()
    out = to_grayscale(img)
    assert len(out.shape) == 2


def test_to_grayscale_already_gray():
    img = make_gray()
    out = to_grayscale(img)
    assert len(out.shape) == 2
    assert out.shape == img.shape


def test_normalize_contrast():
    img = make_bgr()
    out = normalize_contrast(img)
    assert out.shape == (100, 100)
    assert out.dtype == np.uint8


def test_gaussian_blur():
    img = make_gray()
    out = gaussian_blur(img, 3)
    assert out.shape == img.shape


def test_gaussian_blur_even_kernel():
    img = make_gray()
    out = gaussian_blur(img, 4)
    assert out.shape == img.shape


def test_median_blur():
    img = make_gray()
    out = median_blur(img, 3)
    assert out.shape == img.shape


def test_threshold_global():
    img = make_gray()
    out = threshold_global(img)
    assert out.dtype == np.uint8
    assert set(np.unique(out)).issubset({0, 255})


def test_threshold_adaptive():
    img = make_gray()
    out = threshold_adaptive(img)
    assert out.dtype == np.uint8


def test_threshold_otsu():
    img = make_gray()
    out = threshold_otsu(img)
    assert out.dtype == np.uint8


def test_morphology_open():
    img = threshold_otsu(make_gray())
    out = morphology_open(img)
    assert out.shape == img.shape


def test_morphology_close():
    img = threshold_otsu(make_gray())
    out = morphology_close(img)
    assert out.shape == img.shape


def test_invert():
    img = np.zeros((50, 50), dtype=np.uint8)
    out = invert(img)
    assert np.all(out == 255)


def test_resize_upscale():
    img = make_gray(50, 50)
    out = resize_upscale(img, 2.0)
    assert out.shape == (100, 100)


def test_deskew_returns_same_size():
    img = make_gray(100, 100)
    out = deskew(img)
    assert out.shape == img.shape


def test_run_pipeline():
    img = make_bgr(200, 200)
    settings = {
        "DEFAULT_ROI_X": 0, "DEFAULT_ROI_Y": 0, "DEFAULT_ROI_W": 100, "DEFAULT_ROI_H": 100,
        "THRESHOLD_MODE": "OTSU", "upscale_factor": 1.5,
    }
    out = run_pipeline(img, settings)
    assert len(out.shape) == 2
    assert out.dtype == np.uint8
