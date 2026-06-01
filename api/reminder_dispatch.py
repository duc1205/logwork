"""Gửi nhắc vi phạm logwork qua email (1 email / NV / tuần)."""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass

from ..domain.models import WeeklyReport
from ..infra.data_loader import load_roster_employees
from ..infra.email_client import send_email, smtp_configured
from ..infra.notify import Notification
from .auth_service import JIRA_BASE_URL
from .credential_store import JiraCredentials
from .jira_users import resolve_jira_emails
from .live_data import live_data_dir

logger = logging.getLogger("logwork.reminder_dispatch")


@dataclass
class EmailDispatchResult:
    sent: int = 0
    failed: int = 0
    skipped: int = 0
    mode: str = "disabled"  # smtp | disabled


def employee_emails_for_report(
    report: WeeklyReport,
    creds: JiraCredentials,
) -> dict[str, str]:
    """Map employee_id (lower) → email từ Jira, fallback roster CSV."""
    employee_ids = {d.employee_id.lower() for d in report.discrepancies}
    if not employee_ids:
        return {}

    jira_emails = resolve_jira_emails(JIRA_BASE_URL, creds, sorted(employee_ids))
    roster = {
        e.account_id.lower(): e.email.strip()
        for e in load_roster_employees(live_data_dir())
        if e.email and "@" in e.email
    }

    out: dict[str, str] = {}
    for eid in employee_ids:
        email = jira_emails.get(eid, "").strip() or roster.get(eid, "").strip()
        if email and "@" in email:
            out[eid] = email
    return out


def enrich_notifications_with_email(
    notifications: list[Notification],
    email_by_employee: dict[str, str],
) -> None:
    for n in notifications:
        em = email_by_employee.get(n.employee_id.lower(), "")
        n.recipient_email = em
        if em:
            n.channel = "email"


def _combine_email_body(name: str, items: list[Notification], week_label: str) -> str:
    lines = [
        f"Chào {name},",
        "",
        f"Hệ thống đối soát logwork phát hiện {len(items)} vấn đề trong tuần {week_label}:",
        "",
    ]
    for i, n in enumerate(items, 1):
        lines.append(f"{i}. {n.subject.replace('[Logwork] ', '')}")
        lines.append(n.body)
        lines.append("")
    lines.extend(
        [
            "Vui lòng cập nhật logwork trên Jira (jira.tinhvan.com) sớm nhất có thể.",
            "",
            "— Logwork QA Audit (tự động)",
        ]
    )
    return "\n".join(lines)


def dispatch_violation_emails(
    notifications: list[Notification],
    email_by_employee: dict[str, str],
    *,
    week_label: str,
) -> EmailDispatchResult:
    """Gửi 1 email tổng hợp cho mỗi NV có vi phạm."""
    if not notifications:
        return EmailDispatchResult(mode="smtp" if smtp_configured() else "disabled")

    if not smtp_configured():
        logger.info("Email nhắc bỏ qua: chưa cấu hình LOGWORK_SMTP_HOST")
        unique = len({n.employee_id for n in notifications})
        return EmailDispatchResult(skipped=unique, mode="disabled")

    grouped: dict[str, list[Notification]] = defaultdict(list)
    for n in notifications:
        grouped[n.employee_id.lower()].append(n)

    sent = failed = skipped = 0
    for eid, items in grouped.items():
        to_addr = email_by_employee.get(eid, "")
        if not to_addr:
            logger.warning("Không có email cho %s — bỏ qua gửi", eid)
            skipped += 1
            continue
        name = items[0].display_name
        subject = f"[Logwork] Nhắc đối soát tuần {week_label}"
        body = _combine_email_body(name, items, week_label)
        if send_email(to=to_addr, subject=subject, body=body):
            sent += 1
            logger.info("Email nhắc → %s (%s), %d mục", to_addr, eid, len(items))
        else:
            failed += 1

    return EmailDispatchResult(sent=sent, failed=failed, skipped=skipped, mode="smtp")
