"""Job nhắc nhở 17:00 thứ Tư — Jira live + email NV vi phạm."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from ..domain.period_utils import week_range
from ..infra.notify import build_notifications
from .credential_store import JiraCredentials, jira_creds_from_env
from .notification_store import save_notification_batch
from .period_query import resolve_period
from .reminder_dispatch import (
    dispatch_violation_emails,
    employee_emails_for_report,
    enrich_notifications_with_email,
)
from .report_fetch import fetch_team_report

logger = logging.getLogger("logwork.wednesday_job")
TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def next_wednesday_17h(from_dt: datetime | None = None) -> datetime:
    now = from_dt or datetime.now(TZ)
    days_ahead = (2 - now.weekday()) % 7
    candidate = now.replace(hour=17, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate


def run_wednesday_reminder_job(
    *,
    anchor_date: date | None = None,
    creds: JiraCredentials | None = None,
) -> dict:
    """Đối soát tuần + gửi email nhắc NV vi phạm/thiếu log."""
    ref = anchor_date or date.today()
    week_start, week_end = week_range(ref)

    live_creds = creds or jira_creds_from_env()
    if live_creds is None:
        logger.warning(
            "Wednesday job skipped: không có Jira credentials (đăng nhập QA hoặc JIRA_USERNAME/JIRA_API_TOKEN)"
        )
        return {
            "skipped": True,
            "reason": "no_credentials",
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "notifications_count": 0,
            "emails_sent": 0,
            "ran_at": datetime.now(TZ).isoformat(),
        }

    period = resolve_period(start=week_start, end=week_end)
    report, source, _as_of = fetch_team_report(live_creds, period)
    notifications = build_notifications(report)

    week_label = f"{report.week_start.isoformat()} → {report.week_end.isoformat()}"
    email_map = employee_emails_for_report(report, live_creds)
    email_result = dispatch_violation_emails(
        notifications, email_map, week_label=week_label,
    )
    enrich_notifications_with_email(notifications, email_map)

    batch_path = save_notification_batch(
        week_start=report.week_start,
        week_end=report.week_end,
        notifications=notifications,
        data_source=source,
    )
    logger.info(
        "Wednesday job (Jira %s): week=%s..%s notifications=%d emails_sent=%d",
        source,
        report.week_start,
        report.week_end,
        len(notifications),
        email_result.sent,
    )
    return {
        "week_start": report.week_start.isoformat(),
        "week_end": report.week_end.isoformat(),
        "notifications_count": len(notifications),
        "emails_sent": email_result.sent,
        "emails_failed": email_result.failed,
        "emails_skipped": email_result.skipped,
        "email_mode": email_result.mode,
        "batch_path": str(batch_path),
        "data_source": source,
        "paths": {},
        "ran_at": datetime.now(TZ).isoformat(),
    }
