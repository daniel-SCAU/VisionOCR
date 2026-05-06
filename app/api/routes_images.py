import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/images/{inspection_id}")
def get_image(inspection_id: int, kind: str = "raw"):
    from app.services.image_store import ImageStore
    from app.config import Settings
    settings = Settings()
    store = ImageStore(settings.IMAGE_STORAGE_PATH)
    path = store.get_image_path(inspection_id, kind)
    if not path or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(path, media_type="image/jpeg")
