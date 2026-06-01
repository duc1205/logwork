"""Gửi email nhắc logwork qua SMTP."""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

logger = logging.getLogger("logwork.email")


def smtp_configured() -> bool:
    return bool(os.environ.get("LOGWORK_SMTP_HOST", "").strip())


def _smtp_settings() -> dict:
    return {
        "host": os.environ.get("LOGWORK_SMTP_HOST", "").strip(),
        "port": int(os.environ.get("LOGWORK_SMTP_PORT", "587")),
        "user": os.environ.get("LOGWORK_SMTP_USER", "").strip(),
        "password": os.environ.get("LOGWORK_SMTP_PASSWORD", "").strip(),
        "from_addr": os.environ.get("LOGWORK_EMAIL_FROM", "").strip()
        or os.environ.get("LOGWORK_SMTP_USER", "").strip(),
        "from_name": os.environ.get("LOGWORK_EMAIL_FROM_NAME", "Logwork QA Audit").strip(),
        "use_tls": os.environ.get("LOGWORK_SMTP_TLS", "1") != "0",
    }


def send_email(*, to: str, subject: str, body: str) -> bool:
    """Gửi email text/plain. Trả False nếu lỗi."""
    if not smtp_configured():
        return False
    cfg = _smtp_settings()
    if not cfg["from_addr"]:
        logger.warning("LOGWORK_EMAIL_FROM chưa cấu hình")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((cfg["from_name"], cfg["from_addr"]))
    msg["To"] = to

    try:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as smtp:
            if cfg["use_tls"]:
                smtp.starttls()
            if cfg["user"] and cfg["password"]:
                smtp.login(cfg["user"], cfg["password"])
            smtp.sendmail(cfg["from_addr"], [to], msg.as_string())
        return True
    except Exception as exc:
        logger.warning("SMTP send failed to %s: %s", to, exc)
        return False
