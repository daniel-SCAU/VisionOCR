import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.database import Base, get_session_local
from app.main import app
from app.deps import get_db, get_settings


@pytest.fixture
def sample_image() -> np.ndarray:
    """640x480 grayscale ndarray with synthetic 'text' regions."""
    img = np.ones((480, 640), dtype=np.uint8) * 255
    img[100:140, 50:300] = 0
    img[200:240, 50:400] = 0
    return img


@pytest.fixture
def sample_bgr_image() -> np.ndarray:
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200
    img[100:140, 50:300] = 0
    return img


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        APP_ENV="test",
        DATABASE_URL="sqlite:///:memory:",
        IMAGE_STORAGE_PATH="./test_images",
        CAMERA_BACKEND="mock",
        OCR_ENGINE="TESSERACT",
        MIN_CONFIDENCE=60.0,
        SAVE_PASS_IMAGES=False,
        SAVE_FAIL_IMAGES=False,
        DEFAULT_ROI_X=0,
        DEFAULT_ROI_Y=0,
        DEFAULT_ROI_W=640,
        DEFAULT_ROI_H=480,
        CAPTURE_MODE="SINGLE",
        CAPTURE_N_FRAMES=3,
    )


@pytest.fixture
def in_memory_db():
    import app.models  # noqa: F401 — ensure models are registered with Base.metadata
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture
def test_client(test_settings, in_memory_db):
    def override_settings():
        return test_settings

    def override_db():
        yield in_memory_db

    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
