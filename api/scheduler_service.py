"""APScheduler — job nhắc 17:00 thứ Tư (Asia/Ho_Chi_Minh)."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from ..paths import OUTPUT_DIR
from .credential_store import jira_creds_from_env
from .wednesday_job import next_wednesday_17h, run_wednesday_reminder_job

logger = logging.getLogger("logwork.scheduler")
TZ = ZoneInfo("Asia/Ho_Chi_Minh")
JOB_ID = "wednesday_reminder"
STATE_PATH = OUTPUT_DIR / "scheduler_wednesday_state.json"

_scheduler: BackgroundScheduler | None = None


def scheduler_enabled() -> bool:
    return os.environ.get("LOGWORK_DISABLE_SCHEDULER", "0") != "1"


def _load_state() -> dict:
    if not STATE_PATH.is_file():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(*, ran_at: str, result: dict | None, ok: bool) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_run_at": ran_at,
        "last_run_ok": ok,
        "last_result": result,
    }
    STATE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_job_log(result: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ).strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"scheduler_wednesday_reminder_{stamp}.log"
    lines = [
        "job=wednesday_reminder",
        f"ran_at={datetime.now(TZ).isoformat()}",
        f"week={result.get('week_start')}..{result.get('week_end')}",
        f"notifications={result.get('notifications_count', 0)}",
        f"emails_sent={result.get('emails_sent', 0)}",
        f"emails_failed={result.get('emails_failed', 0)}",
        f"emails_skipped={result.get('emails_skipped', 0)}",
        f"skipped={result.get('skipped', False)}",
        f"reason={result.get('reason', '')}",
        f"data_source={result.get('data_source', '')}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def execute_wednesday_reminder_job(**kwargs) -> dict:
    """Chạy job nhắc + ghi log/state (scheduler hoặc admin trigger)."""
    ran_at = datetime.now(TZ).isoformat()
    try:
        result = run_wednesday_reminder_job(**kwargs)
        ok = not result.get("skipped")
        _save_state(ran_at=ran_at, result=result, ok=ok)
        _write_job_log(result)
        return result
    except Exception:
        _save_state(ran_at=ran_at, result=None, ok=False)
        raise


def _run_wednesday_job() -> None:
    try:
        execute_wednesday_reminder_job()
    except Exception:
        logger.exception("Wednesday reminder job failed")


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    if not scheduler_enabled():
        logger.info("Scheduler disabled (LOGWORK_DISABLE_SCHEDULER=1)")
        return None
    if _scheduler is not None:
        return _scheduler

    sched = BackgroundScheduler(timezone=TZ)
    sched.add_job(
        _run_wednesday_job,
        CronTrigger(day_of_week="wed", hour=17, minute=0, timezone=TZ),
        id=JOB_ID,
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=6 * 3600,
    )
    sched.start()
    _scheduler = sched
    nxt = sched.get_job(JOB_ID).next_run_time
    logger.info("Scheduler started: Wed 17:00 %s — next run %s", TZ, nxt)
    return sched


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None


def get_schedule_info() -> dict:
    """Trạng thái lịch nhắc cho UI/API."""
    state = _load_state()
    last_run_at = state.get("last_run_at")
    creds_ok = jira_creds_from_env() is not None
    enabled = scheduler_enabled() and _scheduler is not None

    next_run = next_wednesday_17h()
    if _scheduler is not None:
        job = _scheduler.get_job(JOB_ID)
        if job and job.next_run_time:
            next_run = job.next_run_time.astimezone(TZ)

    last_ok = state.get("last_run_ok")
    hint = "Tự động mỗi 17:00 thứ Tư (Asia/Ho_Chi_Minh)"
    if not scheduler_enabled():
        hint += " · Scheduler tắt trên server (LOGWORK_DISABLE_SCHEDULER=1)"
    elif not creds_ok:
        hint += " · Cần JIRA_USERNAME + JIRA_API_TOKEN để job auto chạy"

    return {
        "wednesday_reminder": "Đối soát tuần + gửi thông báo/email cho NV vi phạm",
        "next_run_at": next_run,
        "timezone": str(TZ),
        "cron": "0 17 * * 3",
        "day_of_week": "wednesday",
        "day_of_week_vi": "Thứ Tư",
        "scheduler_enabled": enabled,
        "scheduler_configured": scheduler_enabled(),
        "credentials_configured": creds_ok,
        "last_run_at": last_run_at,
        "last_run_ok": last_ok,
        "schedule_hint": hint,
    }
