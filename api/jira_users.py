"""Tra cứu profile Jira (displayName, email) — cache in-memory."""

from __future__ import annotations

import base64
import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from threading import Lock

from .credential_store import JiraCredentials

logger = logging.getLogger("logwork.jira_users")

_profile_cache: dict[tuple[str, str], "JiraUserProfile"] = {}
_lock = Lock()


@dataclass(frozen=True)
class JiraUserProfile:
    username: str
    display_name: str
    email: str


def resolve_jira_user_profiles(
    base_url: str,
    creds: JiraCredentials,
    usernames: list[str],
) -> dict[str, JiraUserProfile]:
    """username (lower) → profile. Email từ Jira emailAddress."""
    if not usernames:
        return {}

    base = base_url.rstrip("/")
    auth = base64.b64encode(f"{creds.username}:{creds.password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "User-Agent": "LogworkAudit/1.0",
    }

    result: dict[str, JiraUserProfile] = {}
    to_fetch: list[str] = []

    for raw in usernames:
        un = raw.strip().lower()
        if not un:
            continue
        key = (base, un)
        with _lock:
            cached = _profile_cache.get(key)
            if cached:
                result[un] = cached
                continue
        to_fetch.append(un)

    if not to_fetch:
        return result

    def _store(profile: JiraUserProfile) -> None:
        key = (base, profile.username.lower())
        with _lock:
            _profile_cache[key] = profile
        result[profile.username.lower()] = profile

    def _fetch_one(un: str) -> JiraUserProfile:
        return _fetch_user_profile(base, headers, un)

    if len(to_fetch) == 1:
        _store(_fetch_one(to_fetch[0]))
        return result

    workers = min(8, len(to_fetch))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_fetch_one, un): un for un in to_fetch}
        for fut in as_completed(futures):
            un = futures[fut]
            try:
                _store(fut.result())
            except Exception:
                _store(JiraUserProfile(username=un, display_name=un, email=""))

    return result


def resolve_jira_display_names(
    base_url: str,
    creds: JiraCredentials,
    usernames: list[str],
) -> dict[str, str]:
    profiles = resolve_jira_user_profiles(base_url, creds, usernames)
    return {k: v.display_name for k, v in profiles.items()}


def resolve_jira_emails(
    base_url: str,
    creds: JiraCredentials,
    usernames: list[str],
) -> dict[str, str]:
    profiles = resolve_jira_user_profiles(base_url, creds, usernames)
    return {k: v.email for k, v in profiles.items() if v.email}


def _fetch_user_profile(base: str, headers: dict[str, str], username: str) -> JiraUserProfile:
    qs = urllib.parse.urlencode({"username": username})
    url = f"{base}/rest/api/2/user?{qs}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            display = (data.get("displayName") or username).strip()
            email = (data.get("emailAddress") or "").strip()
            if not email and os.environ.get("LOGWORK_EMAIL_GUESS", "0") == "1":
                domain = os.environ.get("LOGWORK_EMAIL_DOMAIN", "tinhvan.vn").strip()
                if domain:
                    email = f"{username.lower()}@{domain}"
            return JiraUserProfile(username=username.lower(), display_name=display, email=email)
    except urllib.error.HTTPError as exc:
        logger.debug("Jira user lookup HTTP %s for %s", exc.code, username)
    except Exception as exc:
        logger.debug("Jira user lookup failed for %s: %s", username, exc)
    return JiraUserProfile(username=username.lower(), display_name=username, email="")
