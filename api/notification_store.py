"""Lưu trữ thông báo tuần (JSON) — phục vụ UI."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from ..infra.notify import Notification, build_notifications
from ..paths import OUTPUT_DIR
from .schemas import NotificationItem, NotificationListResponse

NOTIFICATIONS_DIR = OUTPUT_DIR / "notifications"


def _batch_path(week_start: date) -> Path:
    NOTIFICATIONS_DIR.mkdir(parents=True, exist_ok=True)
    return NOTIFICATIONS_DIR / f"batch_{week_start.isoformat()}.json"


def save_notification_batch(
    *,
    week_start: date,
    week_end: date,
    notifications: list[Notification],
    data_source: str = "plugin_team",
) -> Path:
    items: list[dict] = []
    now = datetime.now(timezone.utc).isoformat()
    for n in notifications:
        work_date = None
        disc_type = None
        if " — " in n.subject:
            parts = n.subject.split(" — ")
            if len(parts) >= 2:
                disc_type = parts[0].replace("[Logwork] ", "")
                try:
                    work_date = parts[1]
                except ValueError:
                    pass
        items.append(
            {
                "id": str(uuid4()),
                "employee_id": n.employee_id,
                "display_name": n.display_name,
                "subject": n.subject,
                "body": n.body,
                "channel": n.channel,
                "recipient_email": n.recipient_email,
                "work_date": work_date,
                "discrepancy_type": disc_type,
                "created_at": now,
            }
        )
    payload = {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "generated_at": now,
        "data_source": data_source,
        "items": items,
    }
    path = _batch_path(week_start)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_notification_batch(week_start: date) -> dict | None:
    path = _batch_path(week_start)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


LIVE_DATA_SOURCES = frozenset({"plugin", "plugin_team"})


def is_live_notification_batch(batch: dict) -> bool:
    """Batch cũ từ mock/CLI không có data_source — bỏ qua, lấy lại từ Jira."""
    source = batch.get("data_source")
    if source is None:
        return False
    return source in LIVE_DATA_SOURCES


def purge_notification_batches() -> int:
    """Xóa mọi batch đã lưu (admin). Trả về số file đã xóa."""
    if not NOTIFICATIONS_DIR.is_dir():
        return 0
    count = 0
    for p in NOTIFICATIONS_DIR.glob("batch_*.json"):
        p.unlink(missing_ok=True)
        count += 1
    return count


def list_available_weeks() -> list[date]:
    if not NOTIFICATIONS_DIR.is_dir():
        return []
    weeks: list[date] = []
    for p in NOTIFICATIONS_DIR.glob("batch_*.json"):
        try:
            weeks.append(date.fromisoformat(p.stem.replace("batch_", "")))
        except ValueError:
            continue
    return sorted(weeks, reverse=True)


def notifications_from_report(report) -> list[Notification]:
    return build_notifications(report)


def to_response(
    batch: dict,
    *,
    account_id: str | None = None,
    admin: bool = False,
) -> NotificationListResponse:
    items_raw = batch.get("items", [])
    if not admin and account_id:
        items_raw = [i for i in items_raw if i.get("employee_id", "").lower() == account_id.lower()]

    items = [
        NotificationItem(
            id=i["id"],
            employee_id=i["employee_id"],
            display_name=i["display_name"],
            subject=i["subject"],
            body=i["body"],
            channel=i.get("channel", "app"),
            recipient_email=i.get("recipient_email") or None,
            work_date=date.fromisoformat(i["work_date"]) if i.get("work_date") else None,
            discrepancy_type=i.get("discrepancy_type"),
            created_at=datetime.fromisoformat(i["created_at"]),
        )
        for i in items_raw
    ]
    gen = batch.get("generated_at")
    return NotificationListResponse(
        week_start=date.fromisoformat(batch["week_start"]),
        week_end=date.fromisoformat(batch["week_end"]),
        generated_at=datetime.fromisoformat(gen) if gen else None,
        data_source=batch.get("data_source"),
        total=len(items),
        items=items,
    )
