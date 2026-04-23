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

## Quick Start
```bash
pip install -e ".[dev]"
python scripts/migrate.py
uvicorn app.main:app --reload
```

## Running Tests
```bash
pytest tests/ -x -q
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
