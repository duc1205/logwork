"""Lưu Jira credentials theo session (in-memory, TTL)."""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass

from .auth_service import JWT_EXPIRE_HOURS


@dataclass
class JiraCredentials:
    username: str
    password: str


_store: dict[str, tuple[JiraCredentials, float]] = {}
_lock = threading.Lock()
_TTL_SEC = JWT_EXPIRE_HOURS * 3600


def save(account_id: str, username: str, password: str) -> None:
    creds = JiraCredentials(username=username, password=password)
    expires = time.time() + _TTL_SEC
    with _lock:
        _store[account_id.lower()] = (creds, expires)


def get(account_id: str) -> JiraCredentials | None:
    key = account_id.lower()
    with _lock:
        item = _store.get(key)
        if not item:
            return None
        creds, expires = item
        if time.time() > expires:
            _store.pop(key, None)
            return None
        return creds


def delete(account_id: str) -> None:
    with _lock:
        _store.pop(account_id.lower(), None)


def jira_creds_from_env() -> JiraCredentials | None:
    """Scheduler/CLI: JIRA_USERNAME + JIRA_API_TOKEN (hoặc JIRA_PASSWORD)."""
    username = (
        os.environ.get("JIRA_USERNAME", "").strip()
        or os.environ.get("JIRA_EMAIL", "").strip()
    )
    password = (
        os.environ.get("JIRA_API_TOKEN", "").strip()
        or os.environ.get("JIRA_PASSWORD", "").strip()
    )
    if username and password:
        return JiraCredentials(username=username, password=password)
    return None
