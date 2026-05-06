#!/usr/bin/env python3
"""Seed default runtime settings into the database."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import Setting
from datetime import datetime, timezone

DEFAULTS = {
    "ROI_X": "0",
    "ROI_Y": "0",
    "ROI_W": "640",
    "ROI_H": "480",
    "THRESHOLD_MODE": "OTSU",
    "BLUR_KERNEL": "3",
    "MORPH_KERNEL_SIZE": "3",
    "DATE_REGEX": r"(\d{2}[./]\d{2}[./]\d{4}|\d{6}|\d{4}-\d{2}-\d{2})",
    "BATCH_REGEX": r"([A-Z]{1,3}\d{4,8})",
    "MIN_CONFIDENCE": "60.0",
    "CAPTURE_COUNT": "1",
    "CAPTURE_MODE": "SINGLE",
    "EXPECTED_DATE_FORMAT": "DD.MM.YYYY",
    "OCR_WHITELIST": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ./-",
    "USE_DESKEW": "true",
    "USE_IMAGE_REGISTRATION": "false",
    "UPSCALE_FACTOR": "2.0",
}


def seed():
    """Insert default settings if they don't already exist."""
    init_db()
    db = SessionLocal()
    try:
        inserted = 0
        for key, value in DEFAULTS.items():
            existing = db.query(Setting).filter(Setting.key == key).first()
            if existing is None:
                db.add(Setting(key=key, value=value, updated_at=datetime.now(timezone.utc)))
                inserted += 1
        db.commit()
        print(f"Seeded {inserted} settings (skipped {len(DEFAULTS) - inserted} existing).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
