import logging
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class CameraBackend(ABC):
    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def capture(self) -> np.ndarray: ...

    @abstractmethod
    def release(self) -> None: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


class OpenCVCameraBackend(CameraBackend):
    def __init__(self, device_id: int = 0, width: int = 1280, height: int = 720,
                 exposure: float = -6.0, gain: float = 0.0):
        self._device_id = device_id
        self._width = width
        self._height = height
        self._exposure = exposure
        self._gain = gain
        self._cap = None

    @property
    def name(self) -> str:
        return f"opencv:{self._device_id}"

    def open(self) -> None:
        import cv2
        from app.core.exceptions import CameraInitError
        self._cap = cv2.VideoCapture(self._device_id)
        if not self._cap.isOpened():
            raise CameraInitError(f"Cannot open camera device {self._device_id}")
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        if self._exposure != 0:
            self._cap.set(cv2.CAP_PROP_EXPOSURE, self._exposure)
        if self._gain != 0:
            self._cap.set(cv2.CAP_PROP_GAIN, self._gain)
        logger.info("Camera %s opened.", self.name)

    def capture(self) -> np.ndarray:
        import cv2
        from app.core.exceptions import CaptureError
        if self._cap is None or not self._cap.isOpened():
            raise CaptureError("Camera not opened.")
        ret, frame = self._cap.read()
        if not ret or frame is None:
            raise CaptureError("Failed to capture frame.")
        return frame

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        logger.info("Camera %s released.", self.name)


class MockCameraBackend(CameraBackend):
    """Used in tests / when no camera is present."""
    def __init__(self, width: int = 640, height: int = 480):
        self._width = width
        self._height = height

    @property
    def name(self) -> str:
        return "mock"

    def open(self) -> None:
        logger.info("Mock camera opened.")

    def capture(self) -> np.ndarray:
        return np.zeros((self._height, self._width, 3), dtype=np.uint8)

    def release(self) -> None:
        logger.info("Mock camera released.")


def get_camera_backend(settings) -> CameraBackend:
    backend = settings.CAMERA_BACKEND.lower()
    if backend == "mock":
        return MockCameraBackend(settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
    return OpenCVCameraBackend(
        device_id=settings.CAMERA_DEVICE_ID,
        width=settings.CAMERA_WIDTH,
        height=settings.CAMERA_HEIGHT,
        exposure=settings.CAMERA_EXPOSURE,
        gain=settings.CAMERA_GAIN,
    )
