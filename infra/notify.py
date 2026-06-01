"""Sinh nhắc nhở Teams/email từ kết quả đối soát (mock gửi → file)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..domain.models import DiscrepancyType, WeeklyReport
from .reminder_templates import build_reminder


@dataclass
class Notification:
    employee_id: str
    display_name: str
    channel: str  # email | teams | app
    subject: str
    body: str
    recipient_email: str = ""


def build_notifications(report: WeeklyReport) -> list[Notification]:
    """Tạo danh sách nhắc cho NV có vi phạm (trừ compensation-only)."""
    by_id = {s.employee_id: s.display_name for s in report.summaries}
    notify_types = {
        DiscrepancyType.MISSING_DAY,
        DiscrepancyType.UNDER_HOURS,
        DiscrepancyType.OVER_HOURS,
        DiscrepancyType.COMPENSATION,
        DiscrepancyType.HOLIDAY_LOGGED,
        DiscrepancyType.LEAVE_VIOLATION,
    }
    seen: set[tuple[str, str, str]] = set()
    notifications: list[Notification] = []

    for d in report.discrepancies:
        if d.discrepancy_type not in notify_types:
            continue
        key = (d.employee_id, d.work_date.isoformat(), d.discrepancy_type.value)
        if key in seen:
            continue
        seen.add(key)

        name = by_id.get(d.employee_id, d.employee_id)
        body = build_reminder(d, name)
        notifications.append(
            Notification(
                employee_id=d.employee_id,
                display_name=name,
                channel="app",
                subject=f"[Logwork] {d.discrepancy_type.value} — {d.work_date.isoformat()}",
                body=body,
            )
        )
    return notifications


def export_notifications(
    notifications: list[Notification],
    output_dir: Path,
    *,
    week_label: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"reminders_{week_label}.txt"
    lines = [
        f"# Logwork reminders — generated {datetime.now().isoformat(timespec='seconds')}",
        f"# Total: {len(notifications)}",
        "",
    ]
    for i, n in enumerate(notifications, 1):
        lines.extend(
            [
                f"--- [{i}] {n.channel.upper()} -> {n.display_name} ({n.employee_id}) ---",
                f"Subject: {n.subject}",
                n.body,
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
