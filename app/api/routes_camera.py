import io
import cv2
import numpy as np
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.deps import get_settings
from app.schemas import CameraTestResult, OCRResult

router = APIRouter()


@router.get("/camera/frame")
def get_frame(settings=Depends(get_settings)):
    from app.services.acquisition import get_camera_backend
    from app.core.exceptions import CaptureError, CameraInitError
    try:
        cam = get_camera_backend(settings)
        cam.open()
        frame = cam.capture()
        cam.release()
        _, buf = cv2.imencode(".jpg", frame)
        return StreamingResponse(io.BytesIO(buf.tobytes()), media_type="image/jpeg")
    except (CaptureError, CameraInitError) as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/camera/test-capture", response_model=CameraTestResult)
def test_capture(settings=Depends(get_settings)):
    from app.services.acquisition import get_camera_backend
    from app.core.exceptions import CaptureError, CameraInitError
    try:
        cam = get_camera_backend(settings)
        cam.open()
        frame = cam.capture()
        cam.release()
        h, w = frame.shape[:2]
        return CameraTestResult(success=True, message="Capture OK", width=w, height=h)
    except (CaptureError, CameraInitError) as exc:
        return CameraTestResult(success=False, message=str(exc))


@router.post("/camera/test-ocr", response_model=OCRResult)
def test_ocr(settings=Depends(get_settings)):
    from app.services.acquisition import get_camera_backend
    from app.services.ocr import get_ocr_backend
    from app.services import preprocess
    from app.core.exceptions import CaptureError, CameraInitError, OCRExecutionError
    try:
        cam = get_camera_backend(settings)
        cam.open()
        frame = cam.capture()
        cam.release()
        settings_dict = settings.model_dump()
        processed = preprocess.run_pipeline(frame, settings_dict)
        ocr = get_ocr_backend(settings)
        return ocr.recognize(processed)
    except (CaptureError, CameraInitError, OCRExecutionError) as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=str(exc))
