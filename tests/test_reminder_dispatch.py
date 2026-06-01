"""Tests gửi email nhắc vi phạm logwork."""

from __future__ import annotations

from unittest.mock import patch

from logwork.api.reminder_dispatch import dispatch_violation_emails
from logwork.infra.notify import Notification


def _note(eid: str, name: str, subject: str, body: str) -> Notification:
    return Notification(
        employee_id=eid,
        display_name=name,
        channel="app",
        subject=subject,
        body=body,
    )


def test_dispatch_groups_one_email_per_employee():
    notes = [
        _note("alice", "Alice", "[Logwork] MISSING_DAY — 2026-05-26", "Thiếu log ngày 26/5"),
        _note("alice", "Alice", "[Logwork] UNDER_HOURS — 2026-05-27", "Thiếu giờ ngày 27/5"),
        _note("bob", "Bob", "[Logwork] OVER_HOURS — 2026-05-26", "Vượt giờ ngày 26/5"),
    ]
    email_map = {"alice": "alice@tinhvan.vn", "bob": "bob@tinhvan.vn"}

    with patch("logwork.api.reminder_dispatch.smtp_configured", return_value=True), patch(
        "logwork.api.reminder_dispatch.send_email", return_value=True
    ) as send:
        result = dispatch_violation_emails(
            notes, email_map, week_label="2026-05-26 → 2026-06-01"
        )

    assert result.sent == 2
    assert result.failed == 0
    assert result.skipped == 0
    assert result.mode == "smtp"
    assert send.call_count == 2

    subjects = {c.kwargs["subject"] for c in send.call_args_list}
    assert subjects == {"[Logwork] Nhắc đối soát tuần 2026-05-26 → 2026-06-01"}

    alice_call = next(c for c in send.call_args_list if c.kwargs["to"] == "alice@tinhvan.vn")
    body = alice_call.kwargs["body"]
    assert "2 vấn đề" in body
    assert "MISSING_DAY" in body
    assert "UNDER_HOURS" in body


def test_dispatch_skips_without_smtp_or_email():
    notes = [_note("alice", "Alice", "[Logwork] MISSING_DAY — 2026-05-26", "Thiếu log")]

    with patch("logwork.api.reminder_dispatch.smtp_configured", return_value=False):
        r1 = dispatch_violation_emails(notes, {"alice": "a@x.vn"}, week_label="w")
    assert r1.mode == "disabled"
    assert r1.skipped == 1

    with patch("logwork.api.reminder_dispatch.smtp_configured", return_value=True), patch(
        "logwork.api.reminder_dispatch.send_email", return_value=True
    ) as send:
        r2 = dispatch_violation_emails(notes, {}, week_label="w")
    assert r2.skipped == 1
    assert r2.sent == 0
    send.assert_not_called()


def run_tests() -> None:
    test_dispatch_groups_one_email_per_employee()
    test_dispatch_skips_without_smtp_or_email()
    print("OK: reminder dispatch tests passed")


if __name__ == "__main__":
    run_tests()
