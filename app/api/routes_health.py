from fastapi import APIRouter, Depends
from app.schemas import HealthResponse, MetricsResponse
from app.deps import get_settings
from app.services.metrics import MetricsService

router = APIRouter()
_metrics = MetricsService()


@router.get("/health", response_model=HealthResponse)
def health(settings=Depends(get_settings)):
    return HealthResponse(status="ok", version="0.1.0", env=settings.APP_ENV)


@router.get("/metrics", response_model=MetricsResponse)
def metrics():
    m = _metrics.get_metrics()
    return MetricsResponse(**m)
