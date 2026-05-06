from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./db/vision.db"
    IMAGE_STORAGE_PATH: str = "./images"
    CAMERA_BACKEND: str = "opencv"
    CAMERA_DEVICE_ID: int = 0
    CAMERA_DEVICE_PATH: str = ""  # e.g. /dev/video0 — overrides CAMERA_DEVICE_ID when set
    CAMERA_WIDTH: int = 1920
    CAMERA_HEIGHT: int = 1080
    CAMERA_EXPOSURE: float = -6.0
    CAMERA_GAIN: float = 0.0
    DEFAULT_ROI_X: int = 0
    DEFAULT_ROI_Y: int = 0
    DEFAULT_ROI_W: int = 640
    DEFAULT_ROI_H: int = 480
    UPSCALE_FACTOR: float = 2.0
    OCR_ENGINE: str = "TESSERACT"
    OCR_LANGUAGE: str = "eng"
    MIN_CONFIDENCE: float = 60.0
    SAVE_PASS_IMAGES: bool = True
    SAVE_FAIL_IMAGES: bool = True
    LOG_LEVEL: str = "INFO"
    OCR_PSM: int = 6
    OCR_WHITELIST: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ./-"
    DATE_REGEX: str = r"(\b(?:\d{2}[./-]\d{2}[./-]\d{2,4}|\d{4}[./-]\d{2}[./-]\d{2}|\d{6,8})\b)"
    BATCH_REGEX: str = r"\b([A-Z0-9]{2,4}[-/]?[A-Z0-9]{3,8})\b"
    CAPTURE_MODE: str = "SINGLE"
    CAPTURE_N_FRAMES: int = 5
    THRESHOLD_MODE: str = "OTSU"
    THRESHOLD_GLOBAL_VALUE: int = 127
    THRESHOLD_ADAPTIVE_BLOCK_SIZE: int = 11
    THRESHOLD_ADAPTIVE_C: int = 2

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
