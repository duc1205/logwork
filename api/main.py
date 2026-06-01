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

    logger.info("Logwork API: Jira live only — data dir %s", live_data_dir())
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
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
_cors = [o.strip() for o in _cors if o.strip()]
_allow_lan = os.environ.get("LOGWORK_ALLOW_LAN", "0") == "1"
_origin_regex = r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?$" if _allow_lan else None
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors,
    allow_origin_regex=_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    from .live_data import live_data_dir

    return HealthResponse(
        status="ok",
        mode="jira_live",
        data_dir=str(live_data_dir()),
    )


@app.get("/api/schedule", response_model=ScheduleInfoResponse)
def schedule_info() -> ScheduleInfoResponse:
    return ScheduleInfoResponse(**scheduler_service.get_schedule_info())
