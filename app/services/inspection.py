import logging
import time
from datetime import datetime, timezone
from typing import Optional
import numpy as np

from app.schemas import InspectionResult, OCRResult
from app.core.types import InspectionStatus, CaptureMode
from app.core.exceptions import CaptureError
from app.services import preprocess, quality, validation
from app.services.acquisition import CameraBackend
from app.services.ocr import BaseOCRBackend
from app.services.image_store import ImageStore
from app.services.metrics import MetricsService

logger = logging.getLogger(__name__)


class InspectionService:
    def __init__(
        self,
        camera: CameraBackend,
        ocr: BaseOCRBackend,
        image_store: ImageStore,
        metrics: MetricsService,
        db,
    ):
        self._camera = camera
        self._ocr = ocr
        self._image_store = image_store
        self._metrics = metrics
        self._db = db
        self._next_id = 1

    def run_inspection(self, settings) -> InspectionResult:
        start_ts = datetime.now(timezone.utc)
        start_time = time.monotonic()
        inspection_id = self._next_id
        self._next_id += 1

        try:
            mode_str = getattr(settings, "CAPTURE_MODE", "SINGLE").upper()
            n_frames = int(getattr(settings, "CAPTURE_N_FRAMES", 5))

            if mode_str == CaptureMode.BEST_OF_N:
                raw_frame = self._capture_best_of_n(n_frames)
            elif mode_str == CaptureMode.MEDIAN_FUSION:
                raw_frame = self._capture_median_fusion(n_frames, settings)
            else:
                raw_frame = self._capture_single()

            # Preprocess
            settings_dict = settings.model_dump() if hasattr(settings, "model_dump") else dict(vars(settings))
            processed = preprocess.run_pipeline(raw_frame, settings_dict)

            # OCR
            ocr_result: OCRResult = self._ocr.recognize(processed)

            # Parse
            date_regex = getattr(settings, "DATE_REGEX", r"(\d{2}[./]\d{2}[./]\d{4}|\d{6}|\d{4}-\d{2}-\d{2})")
            batch_regex = getattr(settings, "BATCH_REGEX", r"([A-Z]{1,3}\d{4,8})")
            ocr_result.date_text = validation.parse_date_text(ocr_result.raw_text, date_regex)
            ocr_result.batch_text = validation.parse_batch_text(ocr_result.raw_text, batch_regex)

            # Validate
            val_result = validation.validate_result(ocr_result, settings)
            status = InspectionStatus.PASS if val_result.is_pass else InspectionStatus.FAIL

            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            image_path: Optional[str] = None
            processed_path: Optional[str] = None

            save_pass = getattr(settings, "SAVE_PASS_IMAGES", True)
            save_fail = getattr(settings, "SAVE_FAIL_IMAGES", True)
            if (status == InspectionStatus.PASS and save_pass) or \
               (status == InspectionStatus.FAIL and save_fail):
                image_path = self._image_store.save_inspection_image(inspection_id, raw_frame, "raw")
                processed_path = self._image_store.save_processed_image(inspection_id, processed)

            result = InspectionResult(
                id=inspection_id,
                timestamp=start_ts.isoformat(),
                status=status.value,
                raw_text=ocr_result.raw_text,
                date_text=ocr_result.date_text,
                batch_text=ocr_result.batch_text,
                confidence=ocr_result.confidence,
                camera_name=self._camera.name,
                processing_time_ms=elapsed_ms,
                image_path=image_path,
                processed_image_path=processed_path,
            )

        except CaptureError as exc:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            logger.error("Capture error: %s", exc)
            result = InspectionResult(
                id=inspection_id,
                timestamp=start_ts.isoformat(),
                status=InspectionStatus.ERROR.value,
                error_message=str(exc),
                processing_time_ms=elapsed_ms,
                camera_name=self._camera.name,
            )
        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            logger.exception("Inspection error: %s", exc)
            result = InspectionResult(
                id=inspection_id,
                timestamp=start_ts.isoformat(),
                status=InspectionStatus.ERROR.value,
                error_message=str(exc),
                processing_time_ms=elapsed_ms,
            )

        self._metrics.record_inspection(result)
        return result

    def _capture_single(self) -> np.ndarray:
        return self._camera.capture()

    def _capture_best_of_n(self, n: int) -> np.ndarray:
        frames = []
        for _ in range(n):
            try:
                frames.append(self._camera.capture())
            except CaptureError as exc:
                logger.warning("Frame capture error during best-of-n: %s", exc)
        if not frames:
            raise CaptureError("No frames captured in best-of-n mode.")
        return quality.select_best_frame(frames)

    def _capture_median_fusion(self, n: int, settings) -> np.ndarray:
        x = int(getattr(settings, "DEFAULT_ROI_X", 0))
        y = int(getattr(settings, "DEFAULT_ROI_Y", 0))
        w = int(getattr(settings, "DEFAULT_ROI_W", 640))
        h = int(getattr(settings, "DEFAULT_ROI_H", 480))

        rois = []
        for _ in range(n):
            try:
                frame = self._camera.capture()
                roi = preprocess.crop_roi(frame, x, y, min(w, frame.shape[1] - x), min(h, frame.shape[0] - y))
                rois.append(roi)
            except Exception as exc:
                logger.warning("Frame error in median fusion: %s", exc)

        if not rois:
            raise CaptureError("No frames captured in median fusion mode.")

        min_h = min(r.shape[0] for r in rois)
        min_w = min(r.shape[1] for r in rois)
        rois = [r[:min_h, :min_w] for r in rois]
        stacked = np.stack(rois, axis=0).astype(np.float64)
        return np.median(stacked, axis=0).astype(np.uint8)
