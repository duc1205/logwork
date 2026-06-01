"""FastAPI application — Logwork Audit API."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .jira_errors import JiraFetchError

from .routes import admin, auth, dashboard, notifications, settings
from .schemas import HealthResponse, ScheduleInfoResponse
from . import scheduler_service

logger = logging.getLogger("logwork.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .live_data import live_data_dir

    data_dir = live_data_dir()
    logger.info("Logwork API: Jira live only — data dir %s", data_dir)
    if not (data_dir / "config.json").is_file():
        raise RuntimeError(f"Thiếu config live: {data_dir / 'config.json'}")
    scheduler_service.start_scheduler()
    yield
    scheduler_service.shutdown_scheduler()


app = FastAPI(
    title="Logwork Audit API",
    description="API đối soát logwork — login Jira, tổng hợp tuần, thông báo 17h thứ Tư",
    version="1.0.0",
    lifespan=lifespan,
)

_cors = os.environ.get(
    "LOGWORK_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174",
).split(",")
_cors = [o.strip() for o in _cors if o.strip()]
_allow_lan = os.environ.get("LOGWORK_ALLOW_LAN", "0") == "1"
_lan_origin_regex = (
    r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|"
    r"10\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?$"
)
_cors_kw: dict = {
    "allow_origins": _cors,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if _allow_lan:
    _cors_kw["allow_origin_regex"] = _lan_origin_regex
app.add_middleware(CORSMiddleware, **_cors_kw)

app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(settings.router, prefix="/api")


@app.exception_handler(JiraFetchError)
async def jira_fetch_error_handler(_request: Request, exc: JiraFetchError) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc), "jira_error": exc.detail},
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(_request: Request, exc: FileNotFoundError) -> JSONResponse:
    logger.error("FileNotFoundError: %s", exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc),
            "hint": "Kiểm tra LOGWORK_DATA_DIR hoặc thư mục fixtures/live trong repo.",
        },
    )


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    from .live_data import live_data_dir

    data_dir = live_data_dir()
    config_ready = (data_dir / "config.json").is_file()
    return HealthResponse(
        status="ok" if config_ready else "degraded",
        mode="jira_live",
        data_dir=str(data_dir),
        config_ready=config_ready,
    )


@app.get("/api/schedule", response_model=ScheduleInfoResponse)
def schedule_info() -> ScheduleInfoResponse:
    return ScheduleInfoResponse(**scheduler_service.get_schedule_info())
