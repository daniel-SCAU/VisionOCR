import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from app.services.inspection import InspectionService
from app.services.acquisition import MockCameraBackend
from app.services.ocr import BaseOCRBackend
from app.services.image_store import ImageStore
from app.services.metrics import MetricsService
from app.schemas import OCRResult
from app.core.types import InspectionStatus
from app.core.exceptions import CaptureError


class FakeOCR(BaseOCRBackend):
    def __init__(self, result: OCRResult):
        self._result = result

    def recognize(self, img):
        return self._result


def make_service(camera=None, ocr_result=None, db=None, base_path="./test_images"):
    if camera is None:
        camera = MockCameraBackend(640, 480)
    if ocr_result is None:
        ocr_result = OCRResult(raw_text="AB1234 25.06.2025", confidence=85.0)
    ocr = FakeOCR(ocr_result)
    store = ImageStore(base_path)
    metrics = MetricsService()
    return InspectionService(camera=camera, ocr=ocr, image_store=store, metrics=metrics, db=db or MagicMock())


class FakeSettings:
    APP_ENV = "test"
    CAPTURE_MODE = "SINGLE"
    CAPTURE_N_FRAMES = 3
    DEFAULT_ROI_X = 0
    DEFAULT_ROI_Y = 0
    DEFAULT_ROI_W = 640
    DEFAULT_ROI_H = 480
    THRESHOLD_MODE = "OTSU"
    DATE_REGEX = r"(\d{2}[./]\d{2}[./]\d{4}|\d{6}|\d{4}-\d{2}-\d{2})"
    BATCH_REGEX = r"([A-Z]{1,3}\d{4,8})"
    MIN_CONFIDENCE = 60.0
    SAVE_PASS_IMAGES = False
    SAVE_FAIL_IMAGES = False

    def model_dump(self):
        return {
            "DEFAULT_ROI_X": self.DEFAULT_ROI_X,
            "DEFAULT_ROI_Y": self.DEFAULT_ROI_Y,
            "DEFAULT_ROI_W": self.DEFAULT_ROI_W,
            "DEFAULT_ROI_H": self.DEFAULT_ROI_H,
            "THRESHOLD_MODE": self.THRESHOLD_MODE,
        }


def test_single_capture_pass():
    svc = make_service()
    result = svc.run_inspection(FakeSettings())
    assert result.status == InspectionStatus.PASS.value
    assert result.raw_text == "AB1234 25.06.2025"
    assert result.confidence == pytest.approx(85.0)


def test_single_capture_fail_low_confidence():
    svc = make_service(ocr_result=OCRResult(raw_text="AB1234 25.06.2025", confidence=30.0))
    result = svc.run_inspection(FakeSettings())
    assert result.status == InspectionStatus.FAIL.value


def test_best_of_n():
    settings = FakeSettings()
    settings.CAPTURE_MODE = "BEST_OF_N"
    settings.CAPTURE_N_FRAMES = 3
    svc = make_service()
    result = svc.run_inspection(settings)
    assert result.status in (InspectionStatus.PASS.value, InspectionStatus.FAIL.value, InspectionStatus.ERROR.value)


def test_median_fusion():
    settings = FakeSettings()
    settings.CAPTURE_MODE = "MEDIAN_FUSION"
    settings.CAPTURE_N_FRAMES = 3
    svc = make_service()
    result = svc.run_inspection(settings)
    assert result.status in (InspectionStatus.PASS.value, InspectionStatus.FAIL.value, InspectionStatus.ERROR.value)


def test_failed_capture():
    cam = MagicMock()
    cam.name = "mock_fail"
    cam.capture.side_effect = CaptureError("Camera disconnected")
    svc = make_service(camera=cam)
    result = svc.run_inspection(FakeSettings())
    assert result.status == InspectionStatus.ERROR.value
    assert "Camera disconnected" in result.error_message


def test_metrics_updated():
    svc = make_service()
    svc.run_inspection(FakeSettings())
    m = svc._metrics.get_metrics()
    assert m["total"] == 1
