#!/usr/bin/env python3
"""Run OCR on a single local image file."""
import argparse
import os
import sys

import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.services import preprocess
from app.services.ocr import get_ocr_backend


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OCR on one image file.")
    parser.add_argument("image_path", help="Path to the input image file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_path = os.path.abspath(args.image_path)

    img = cv2.imread(image_path)
    if img is None:
        raise SystemExit(f"Image not found or unreadable: {image_path}")

    settings = get_settings()
    processed = preprocess.run_pipeline(img, settings.model_dump())
    result = get_ocr_backend(settings).recognize(processed)

    print(f"Image: {image_path}")
    print("Text:", result.raw_text)
    print("Confidence:", result.confidence)


if __name__ == "__main__":
    main()
