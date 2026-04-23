from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session
from app.config import Settings
from app.database import get_db


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_inspection_service(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    from app.services.inspection import InspectionService
    from app.services.acquisition import get_camera_backend
    from app.services.ocr import get_ocr_backend
    from app.services.image_store import ImageStore
    from app.services.metrics import MetricsService

    camera = get_camera_backend(settings)
    ocr = get_ocr_backend(settings)
    image_store = ImageStore(settings.IMAGE_STORAGE_PATH)
    metrics = MetricsService()
    return InspectionService(camera=camera, ocr=ocr, image_store=image_store, metrics=metrics, db=db)
