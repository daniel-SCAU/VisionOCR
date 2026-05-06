#!/usr/bin/env python3
"""Run a single inspection end-to-end and print the result."""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.services.acquisition import get_camera_backend
from app.services.ocr import get_ocr_backend
from app.services.image_store import ImageStore
from app.services.metrics import MetricsService
from app.services.inspection import InspectionService


def main():
    settings = get_settings()
    init_db()

    camera = get_camera_backend(settings)
    camera.initialize()

    ocr = get_ocr_backend(settings)
    image_store = ImageStore(base_path=settings.IMAGE_STORAGE_PATH)
    metrics = MetricsService()
    db = SessionLocal()

    service = InspectionService(
        camera=camera,
        ocr=ocr,
        image_store=image_store,
        metrics=metrics,
        db=db,
    )

    try:
        print("Running inspection ...")
        result = service.run_inspection(settings)
        print(json.dumps(result.model_dump(), indent=2, default=str))
        print(f"\nResult: {result.status}")
    finally:
        camera.release()
        db.close()


if __name__ == "__main__":
    main()
