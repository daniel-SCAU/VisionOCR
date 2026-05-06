import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.deps import get_settings, get_db, get_inspection_service
from app.schemas import InspectionResult
from app.core.types import InspectionStatus
from app.config import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base


def make_test_db():
    import app.models  # noqa: F401 — ensure models are registered with Base.metadata
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


@pytest.fixture
def api_client():
    test_settings = Settings(
        APP_ENV="test",
        DATABASE_URL="sqlite:///:memory:",
        IMAGE_STORAGE_PATH="./test_images",
        CAMERA_BACKEND="mock",
    )
    db = make_test_db()

    mock_result = InspectionResult(
        id=1,
        timestamp="2025-01-01T00:00:00+00:00",
        status=InspectionStatus.PASS.value,
        raw_text="AB1234 25.06.2025",
        date_text="25.06.2025",
        batch_text="AB1234",
        confidence=85.0,
        processing_time_ms=42,
    )
    mock_inspection_svc = MagicMock()
    mock_inspection_svc.run_inspection.return_value = mock_result

    def override_db():
        yield db

    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_inspection_service] = lambda: mock_inspection_svc

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    db.close()


def test_health(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_get_config(api_client):
    resp = api_client.get("/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "settings" in data


def test_put_config(api_client):
    payload = {"settings": [{"key": "MIN_CONFIDENCE", "value": "75.0"}]}
    resp = api_client.put("/config", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    keys = [s["key"] for s in data["settings"]]
    assert "MIN_CONFIDENCE" in keys


def test_post_inspect(api_client):
    resp = api_client.post("/inspect")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PASS"
    assert data["raw_text"] == "AB1234 25.06.2025"


def test_get_inspections(api_client):
    resp = api_client.get("/inspections")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
