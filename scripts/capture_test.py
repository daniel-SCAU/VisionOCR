#!/usr/bin/env python3
"""Capture a test frame from the configured camera and save it to disk."""
import sys
import os
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.services.acquisition import get_camera_backend
from app.core.utils import ensure_dir, safe_filename


def main():
    settings = get_settings()
    camera = get_camera_backend(settings)

    print(f"Initializing camera (device={settings.CAMERA_DEVICE_ID}, "
          f"backend={settings.CAMERA_BACKEND}) ...")
    camera.initialize()

    try:
        print("Capturing frame ...")
        frame = camera.capture()
        print(f"Captured frame: {frame.shape[1]}x{frame.shape[0]} px")

        out_dir = "/tmp/capture_test"
        ensure_dir(out_dir)
        filename = safe_filename("capture", "jpg")
        out_path = os.path.join(out_dir, filename)
        cv2.imwrite(out_path, frame)
        print(f"Saved to: {out_path}")
    finally:
        camera.release()
        print("Camera released.")


if __name__ == "__main__":
    main()
