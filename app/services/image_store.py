import os
import logging
from datetime import datetime, timezone
from typing import Optional
import numpy as np
import cv2
from app.core.exceptions import StorageError

logger = logging.getLogger(__name__)


class ImageStore:
    def __init__(self, base_path: str):
        self._base = base_path
        os.makedirs(base_path, exist_ok=True)

    def _day_dir(self) -> str:
        today = datetime.now(timezone.utc)
        path = os.path.join(self._base, today.strftime("%Y/%m/%d"))
        os.makedirs(path, exist_ok=True)
        return path

    def save_inspection_image(self, inspection_id: int, img: np.ndarray, kind: str = "raw") -> str:
        try:
            ts = datetime.now(timezone.utc).strftime("%H%M%S_%f")
            filename = f"{inspection_id}_{ts}_{kind}.jpg"
            path = os.path.join(self._day_dir(), filename)
            cv2.imwrite(path, img)
            logger.debug("Saved %s image to %s", kind, path)
            return path
        except Exception as exc:
            raise StorageError(f"Failed to save image: {exc}") from exc

    def save_processed_image(self, inspection_id: int, img: np.ndarray) -> str:
        return self.save_inspection_image(inspection_id, img, kind="processed")

    def get_image_path(self, inspection_id: int, kind: str = "raw") -> Optional[str]:
        for root, _, files in os.walk(self._base):
            for f in files:
                if f.startswith(f"{inspection_id}_") and f.endswith(f"_{kind}.jpg"):
                    return os.path.join(root, f)
        return None
