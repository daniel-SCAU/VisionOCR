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

## Security Considerations
- This project does not implement authentication/authorization by default.
- **WARNING:** Running on `0.0.0.0` without added auth controls makes the service accessible to anyone on reachable networks, which can allow unauthorized OCR use and access to stored inspection/image data.
- Before exposing the app on a network, add auth controls and restrict access with firewall rules and/or a TLS reverse proxy.

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
> Review **Security Considerations** above before exposing this service beyond localhost.

## Running Tests
```bash
pytest tests/ -x -q
```

## Test an Image (Linux)
Use this to run OCR on a local image file:

```bash
python scripts/test_image.py ./test_image.jpg
```

## Improve OCR Results (Practical Tuning Workflow)
1. Tighten ROI (`DEFAULT_ROI_X/Y/W/H`) so OCR sees only the date/code print area.
2. Compare threshold modes (`THRESHOLD_MODE=OTSU|ADAPTIVE|GLOBAL`) on the same sample set.
3. Stabilize capture quality (fixed lighting/focus) and tune `CAMERA_EXPOSURE`, `CAMERA_GAIN`, `CAMERA_WIDTH`, `CAMERA_HEIGHT`.
4. For noisy scenes, enable multi-frame capture with `CAPTURE_MODE=BEST_OF_N` or `MEDIAN_FUSION` and tune `CAPTURE_N_FRAMES`.
5. Tune Tesseract layout and character constraints using `OCR_PSM`, `OCR_WHITELIST`, and `OCR_LANGUAGE`.
6. Refine `DATE_REGEX` and `BATCH_REGEX` to match real line formats.
7. Calibrate `MIN_CONFIDENCE` from measured confidence distributions (good vs bad samples), not guesswork.
8. Re-validate iteratively with `python scripts/test_image.py ./test_image.jpg` and `/camera/test-ocr`.

### Batch evaluation helper
Use the tuning script to compare preprocessing modes and estimate confidence thresholds:

```bash
python scripts/tune_ocr.py \
  --samples-dir ./samples/all \
  --good-dir ./samples/good \
  --bad-dir ./samples/bad \
  --modes OTSU,ADAPTIVE,GLOBAL
```

Optional ROI / OCR overrides can be provided directly:

```bash
python scripts/tune_ocr.py --samples-dir ./samples/all --roi-x 120 --roi-y 80 --roi-w 560 --roi-h 180 --psm 7
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
