import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.config import Settings
from app.logging_config import setup_logging
from app.database import init_db
from app.deps import get_settings
from app.api import routes_health, routes_config, routes_inspection, routes_history, routes_images, routes_camera

logger = logging.getLogger(__name__)
_templates_dir = os.path.join(os.path.dirname(__file__), "web", "templates")
_static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
templates = Jinja2Templates(directory=_templates_dir)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    setup_logging(settings.LOG_LEVEL)
    init_db(settings)
    logger.info("VisionOCR started (env=%s)", settings.APP_ENV)
    yield
    logger.info("VisionOCR shutting down.")


app = FastAPI(title="VisionOCR", version="0.1.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=_static_dir), name="static")

# API routers
app.include_router(routes_health.router, tags=["health"])
app.include_router(routes_config.router, tags=["config"])
app.include_router(routes_inspection.router, tags=["inspection"])
app.include_router(routes_history.router, tags=["history"])
app.include_router(routes_images.router, tags=["images"])
app.include_router(routes_camera.router, tags=["camera"])


# Web routes
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "settings": settings})


@app.get("/camera", response_class=HTMLResponse)
def camera_page(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("camera.html", {"request": request, "settings": settings})


@app.get("/ocr-tuning", response_class=HTMLResponse)
def ocr_tuning(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("ocr_tuning.html", {"request": request, "settings": settings})


@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("history.html", {"request": request, "settings": settings})


@app.get("/inspections/{inspection_id}/detail", response_class=HTMLResponse)
def inspection_detail(inspection_id: int, request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("inspection_detail.html", {
        "request": request,
        "inspection_id": inspection_id,
        "settings": settings,
    })


@app.get("/system", response_class=HTMLResponse)
def system_page(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("system.html", {"request": request, "settings": settings})
