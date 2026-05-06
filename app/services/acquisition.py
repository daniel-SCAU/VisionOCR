import logging
from abc import ABC, abstractmethod
from typing import Optional, Union
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
    """OpenCV-backed camera.

    *device* can be an integer index (0, 1, …) **or** a Linux V4L2 device path
    string such as ``"/dev/video0"``.  When a path is provided it is passed
    directly to ``cv2.VideoCapture``; this is the preferred form for USB cameras
    on Linux because it ties the handle to a specific physical port rather than
    the enumeration order.

    Auto-exposure is disabled (V4L2 manual mode) whenever *exposure* is non-zero
    so that the configured shutter value is actually applied.
    """

    def __init__(
        self,
        device: Union[int, str] = 0,
        width: int = 1280,
        height: int = 720,
        exposure: float = -6.0,
        gain: float = 0.0,
    ):
        # Accept both integer index and "/dev/videoN" path strings
        self._device: Union[int, str] = device
        self._width = width
        self._height = height
        self._exposure = exposure
        self._gain = gain
        self._cap = None

    @property
    def name(self) -> str:
        return f"opencv:{self._device}"

    def open(self) -> None:
        import cv2
        from app.core.exceptions import CameraInitError

        logger.info("Opening camera device: %s", self._device)
        # Use CAP_V4L2 backend explicitly for Linux path devices to guarantee
        # that V4L2 property names (CAP_PROP_AUTO_EXPOSURE etc.) are honoured.
        if isinstance(self._device, str):
            self._cap = cv2.VideoCapture(self._device, cv2.CAP_V4L2)
        else:
            self._cap = cv2.VideoCapture(self._device)

        if not self._cap.isOpened():
            raise CameraInitError(f"Cannot open camera device {self._device!r}")

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

        if self._exposure != 0:
            # V4L2: CAP_PROP_AUTO_EXPOSURE value 1 = manual, 3 = auto
            self._cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            self._cap.set(cv2.CAP_PROP_EXPOSURE, self._exposure)

        if self._gain != 0:
            self._cap.set(cv2.CAP_PROP_GAIN, self._gain)

        logger.info("Camera %s opened (%dx%d).", self.name, self._width, self._height)

    def capture(self) -> np.ndarray:
        import cv2
        from app.core.exceptions import CaptureError

        if self._cap is None or not self._cap.isOpened():
            raise CaptureError("Camera not opened.")
        ret, frame = self._cap.read()
        if not ret or frame is None:
            raise CaptureError("Failed to capture frame.")
        return frame

    def capture_n_frames(self, n: int) -> list[np.ndarray]:
        """Capture *n* frames in rapid succession."""
        return [self.capture() for _ in range(n)]

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

    def capture_n_frames(self, n: int) -> list[np.ndarray]:
        return [self.capture() for _ in range(n)]

    def release(self) -> None:
        logger.info("Mock camera released.")


def get_camera_backend(settings) -> CameraBackend:
    """Factory: returns the appropriate camera backend from *settings*.

    Resolution order for the device identifier:
    1. ``CAMERA_DEVICE_PATH`` if non-empty (e.g. ``/dev/video0``)
    2. ``CAMERA_DEVICE_ID``  integer index (e.g. ``0``)
    """
    backend = settings.CAMERA_BACKEND.lower()
    if backend == "mock":
        return MockCameraBackend(settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)

    device_path: str = getattr(settings, "CAMERA_DEVICE_PATH", "")
    device: Union[int, str] = device_path.strip() if device_path.strip() else settings.CAMERA_DEVICE_ID

    return OpenCVCameraBackend(
        device=device,
        width=settings.CAMERA_WIDTH,
        height=settings.CAMERA_HEIGHT,
        exposure=settings.CAMERA_EXPOSURE,
        gain=settings.CAMERA_GAIN,
    )
