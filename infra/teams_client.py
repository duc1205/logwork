"""Gửi Teams qua Incoming Webhook (optional — fallback file)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from .notify import Notification


@dataclass
class SendResult:
    sent: int
    failed: int
    mode: str  # webhook | file_only


def get_webhook_url() -> str | None:
    url = os.environ.get("TEAMS_WEBHOOK_URL", "").strip()
    return url or None


def send_teams_message(webhook_url: str, text: str, *, title: str = "Logwork") -> bool:
    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": title,
        "themeColor": "0078D4",
        "title": title,
        "text": text.replace("\n", "<br>"),
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def dispatch_notifications(
    notifications: list[Notification],
    *,
    webhook_url: str | None = None,
) -> SendResult:
    url = webhook_url or get_webhook_url()
    if not url:
        return SendResult(sent=0, failed=0, mode="file_only")

    sent = failed = 0
    for n in notifications:
        ok = send_teams_message(url, n.body, title=n.subject)
        if ok:
            sent += 1
        else:
            failed += 1
    return SendResult(sent=sent, failed=failed, mode="webhook")
