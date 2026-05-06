from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./db/vision.db"
    IMAGE_STORAGE_PATH: str = "./images"
    CAMERA_BACKEND: str = "opencv"
    CAMERA_DEVICE_ID: int = 0
    CAMERA_DEVICE_PATH: str = "/dev/video0"  # preferred Linux USB camera default; overrides CAMERA_DEVICE_ID when set
    CAMERA_WIDTH: int = 1920
    CAMERA_HEIGHT: int = 1080
    CAMERA_EXPOSURE: float = -6.0
    CAMERA_GAIN: float = 0.0
    DEFAULT_ROI_X: int = 0
    DEFAULT_ROI_Y: int = 0
    DEFAULT_ROI_W: int = 640
    DEFAULT_ROI_H: int = 480
    OCR_ENGINE: str = "TESSERACT"
    OCR_LANGUAGE: str = "eng"
    MIN_CONFIDENCE: float = 60.0
    SAVE_PASS_IMAGES: bool = True
    SAVE_FAIL_IMAGES: bool = True
    LOG_LEVEL: str = "INFO"
    OCR_PSM: int = 6
    OCR_WHITELIST: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ./-"
    DATE_REGEX: str = r"(\d{2}[./]\d{2}[./]\d{4}|\d{6}|\d{4}-\d{2}-\d{2})"
    BATCH_REGEX: str = r"([A-Z]{1,3}\d{4,8})"
    CAPTURE_MODE: str = "SINGLE"
    CAPTURE_N_FRAMES: int = 5
    THRESHOLD_MODE: str = "OTSU"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
