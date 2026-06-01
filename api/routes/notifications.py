"""Notification routes."""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Query

from ..auth_service import AuthUser, is_qa_user
from ..credential_store import JiraCredentials
from ..deps import get_current_user, get_jira_credentials, require_admin
from ...infra.notify import Notification, build_notifications
from ..notification_store import (
    is_live_notification_batch,
    list_available_weeks,
    load_notification_batch,
    purge_notification_batches,
    save_notification_batch,
    to_response,
)
from ..period_helpers import effective_as_of_range
from ..period_query import resolve_period
from ..schemas import NotificationItem, NotificationListResponse
from ..user_pipeline import reconcile_for_team, reconcile_for_user
from ..scheduler_service import execute_wednesday_reminder_job

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _notification_items(
    notifications: list[Notification],
    user: AuthUser,
    as_of: date,
) -> list[NotificationItem]:
    now = datetime.now(timezone.utc)
    items: list[NotificationItem] = []
    for n in notifications:
        if not is_qa_user(user) and n.employee_id.lower() != user.account_id.lower():
            continue
        work_date: date | None = None
        disc_type: str | None = None
        if " — " in n.subject:
            parts = n.subject.split(" — ")
            if len(parts) >= 2:
                disc_type = parts[0].replace("[Logwork] ", "")
                try:
                    work_date = date.fromisoformat(parts[1])
                except ValueError:
                    pass
        if work_date is not None and work_date > as_of:
            continue
        items.append(
            NotificationItem(
                id=str(uuid4()),
                employee_id=n.employee_id,
                display_name=n.display_name,
                subject=n.subject,
                body=n.body,
                channel=n.channel,
                recipient_email=getattr(n, "recipient_email", None) or None,
                work_date=work_date,
                discrepancy_type=disc_type,
                created_at=now,
            )
        )
    return items


def _reconcile(user, creds, period):
    if is_qa_user(user):
        if period.mode == "month":
            ym = f"{period.start.year:04d}-{period.start.month:02d}"
            return reconcile_for_team(creds, month=ym)
        return reconcile_for_team(
            creds,
            anchor_date=period.anchor,
            period_start=period.start,
            period_end=period.end,
        )
    if period.mode == "month":
        ym = f"{period.start.year:04d}-{period.start.month:02d}"
        return reconcile_for_user(user, creds, month=ym)
    return reconcile_for_user(
        user,
        creds,
        anchor_date=period.anchor,
        period_start=period.start,
        period_end=period.end,
    )


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    week: date | None = Query(None, description="Ngày trong tuần (legacy)"),
    month: str | None = Query(None, description="Tháng YYYY-MM"),
    start: date | None = Query(None, description="Từ ngày (tuần)"),
    end: date | None = Query(None, description="Đến ngày (tuần)"),
    refresh: bool = Query(False, description="Admin: bỏ cache, lấy lại từ Jira"),
    user: AuthUser = Depends(get_current_user),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> NotificationListResponse:
    period = resolve_period(week=week, month=month, start=start, end=end)
    as_of = effective_as_of_range(period.start, period.end)

    use_cache = period.mode == "week" and not refresh
    if use_cache:
        batch = load_notification_batch(period.start)
        if batch is not None and is_live_notification_batch(batch):
            resp = to_response(
                batch,
                account_id=user.account_id,
                admin=is_qa_user(user),
            )
            items = [
                i for i in resp.items
                if i.work_date is None or i.work_date <= as_of
            ]
            return resp.model_copy(update={"items": items, "total": len(items)})

    report, source = _reconcile(user, creds, period)
    notifications = build_notifications(report)

    if period.mode == "week" and notifications:
        save_notification_batch(
            week_start=report.week_start,
            week_end=report.week_end,
            notifications=notifications,
            data_source=source,
        )

    items = _notification_items(notifications, user, as_of)
    return NotificationListResponse(
        week_start=period.start,
        week_end=period.end,
        generated_at=None,
        data_source=source,
        total=len(items),
        items=items,
    )


@router.get("/weeks")
def notification_weeks(_user: AuthUser = Depends(get_current_user)) -> dict:
    weeks = [d.isoformat() for d in list_available_weeks()]
    return {"weeks": weeks, "count": len(weeks)}


@router.post("/purge", dependencies=[Depends(require_admin)])
def purge_notification_cache(_user: AuthUser = Depends(get_current_user)) -> dict:
    """Admin: xóa batch thông báo cũ (mock/CLI). Lần sau sẽ lấy từ Jira."""
    removed = purge_notification_batches()
    return {"purged": removed, "message": f"Đã xóa {removed} batch thông báo đã lưu"}


@router.post("/trigger", dependencies=[Depends(require_admin)])
def trigger_wednesday_job(
    week: date | None = Query(None),
    user: AuthUser = Depends(get_current_user),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> dict:
    """Admin/QA: chạy job nhắc từ dữ liệu Jira live."""
    return execute_wednesday_reminder_job(anchor_date=week, creds=creds)
