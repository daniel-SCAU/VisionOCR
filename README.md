# VisionOCR

Industrial-grade OCR inspection application for Linux.

## Features
- Real-time camera capture with OpenCV (or mock backend for testing)
- Image preprocessing pipeline: ROI crop, grayscale, deskew, threshold, morphology, upscale
- Tesseract OCR integration with configurable PSM and whitelist
- Date and batch-code regex extraction and validation
- PASS/FAIL/ERROR inspection result with confidence scoring
- SQLite-backed inspection history
- FastAPI REST API with Jinja2 web dashboard
- Systemd service unit for production deployment

## Linux Install & Run
```bash
# Ubuntu/Debian system deps
sudo apt update
sudo apt install -y python3 python3-venv tesseract-ocr
# Requires Python >= 3.11 (see pyproject.toml). Tesseract 4+ is recommended.

# Project setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Init database
python scripts/migrate.py

# Run API server
uvicorn app.main:app --host 0.0.0.0 --reload
```

Open `http://<server-ip>:8000` after startup.
For local access, you can still use `http://127.0.0.1:8000`.
To find your server IP on Linux, run `hostname -I`.

> Security note: Binding to `0.0.0.0` exposes the service on all network interfaces.
> This project does not enable authentication/authorization by default. Do not expose this service to untrusted networks unless you add auth controls first; also restrict access with firewall rules and/or place the app behind a reverse proxy with TLS.

## Running Tests
```bash
pytest tests/ -x -q
```

## Test an Image (Linux)
Use this to run OCR on a local image file:

```bash
python - <<'PY'
import cv2
from app.config import get_settings
from app.services import preprocess
from app.services.ocr import get_ocr_backend

# Replace with your file (example: ./test_image.jpg)
img = cv2.imread("./test_image.jpg")
if img is None:
    raise SystemExit("Image not found.")

settings = get_settings()
# Applies ROI + thresholding + morphology pipeline before OCR.
processed = preprocess.run_pipeline(img, settings.model_dump())
result = get_ocr_backend(settings).recognize(processed)
print("Text:", result.raw_text)
print("Confidence:", result.confidence)
PY
```

## API Endpoints
- `GET /health` — Health check
- `GET /metrics` — Inspection metrics
- `POST /inspect` — Run inspection
- `GET /inspections` — List inspection history
- `GET /config` — Get configuration
- `PUT /config` — Update configuration
- `GET /camera/frame` — Live camera frame
- `POST /camera/test-capture` — Test camera capture
- `POST /camera/test-ocr` — Test OCR on live frame

---
