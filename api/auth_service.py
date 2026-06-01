"""Xác thực Jira + JWT session — chỉ tài khoản Jira thật."""

from __future__ import annotations

import base64
import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from ..infra.data_loader import load_roster_employees
from .live_data import live_data_dir

logger = logging.getLogger("logwork.auth")

JWT_SECRET = os.environ.get("LOGWORK_JWT_SECRET", "logwork-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.environ.get("LOGWORK_JWT_EXPIRE_HOURS", "12"))
JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL", "https://jira.tinhvan.com").rstrip("/")
JIRA_API_VERSION = int(os.environ.get("JIRA_API_VERSION", "2"))
ADMIN_USERS = {
    u.strip().lower()
    for u in os.environ.get("LOGWORK_ADMIN_USERS", "").split(",")
    if u.strip()
}
QA_USERS = {
    u.strip().lower()
    for u in os.environ.get("LOGWORK_QA_USERS", "").split(",")
    if u.strip()
}
# QA tự động gồm admin cấu hình (không liên quan quyền Administrator trên Jira)
QA_USERS |= ADMIN_USERS


def _role_for_account(account_id: str) -> str:
    """admin = cấu hình Logwork (LOGWORK_ADMIN_USERS); không phải Jira Administrator."""
    aid = account_id.lower()
    if aid in ADMIN_USERS:
        return "admin"
    if aid in QA_USERS:
        return "qa"
    return "employee"


def refresh_user_role(user: AuthUser) -> AuthUser:
    """Luôn đọc lại role từ env — không tin role cũ trong JWT."""
    role = _role_for_account(user.account_id)
    if user.role == role:
        return user
    return AuthUser(
        account_id=user.account_id,
        display_name=user.display_name,
        email=user.email,
        team=user.team,
        center=user.center,
        role=role,
    )


def is_qa_user(user: AuthUser) -> bool:
    return user.role in ("admin", "qa")


def is_settings_admin(user: AuthUser) -> bool:
    return user.role == "admin"


@dataclass
class AuthUser:
    account_id: str
    display_name: str
    email: str = ""
    team: str | None = None
    center: str | None = None
    role: str = "employee"


@dataclass
class AuthResult:
    user: AuthUser | None = None
    error: str | None = None


def _jira_myself(username: str, password: str) -> AuthResult:
    """Xác thực bằng Jira REST /myself — username + password của chính user."""
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    url = f"{JIRA_BASE_URL}/rest/api/{JIRA_API_VERSION}/myself"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
            "User-Agent": "LogworkAudit/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            profile = json.loads(resp.read().decode("utf-8"))
            return AuthResult(user=_profile_to_user(profile))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:200]
        logger.warning("Jira auth HTTP %s for user=%s: %s", exc.code, username, body)
        if exc.code in (401, 403):
            return AuthResult(error="Sai username hoặc mật khẩu Jira")
        return AuthResult(error=f"Jira trả về lỗi HTTP {exc.code}")
    except urllib.error.URLError as exc:
        logger.warning("Jira unreachable: %s", exc.reason)
        return AuthResult(
            error=f"Không kết nối được Jira ({JIRA_BASE_URL}). Kiểm tra mạng/VPN."
        )
    except TimeoutError:
        return AuthResult(error="Jira không phản hồi (timeout). Thử lại sau.")
    except Exception as exc:
        logger.exception("Jira auth unexpected error")
        return AuthResult(error=f"Lỗi xác thực Jira: {exc}")


def _profile_to_user(profile: dict) -> AuthUser:
    """Map Jira /myself → AuthUser. Ưu tiên field `name` (Jira Server username)."""
    account_id = (profile.get("name") or profile.get("key") or "").strip()
    if not account_id:
        account_id = profile.get("emailAddress", "unknown").split("@")[0]
    account_id = account_id.lower()
    display = profile.get("displayName") or account_id
    email = profile.get("emailAddress") or ""

    roster = load_roster_employees(live_data_dir())
    emp = next((e for e in roster if e.account_id.lower() == account_id), None)
    if emp:
        return AuthUser(
            account_id=emp.account_id,
            display_name=display or emp.display_name or account_id,
            email=emp.email or email,
            team=emp.team,
            center=emp.center,
            role=_role_for_account(account_id),
        )
    return AuthUser(
        account_id=account_id,
        display_name=display,
        email=email,
        role=_role_for_account(account_id),
    )


def authenticate(username: str, password: str) -> AuthResult:
    """
    Đăng nhập bằng username + password Jira của chính user.
    Gọi GET /rest/api/2/myself — không hỗ trợ mock/demo.
    """
    uname = username.strip()
    if not uname or not password:
        return AuthResult(error="Username và mật khẩu không được để trống")

    if os.environ.get("LOGWORK_MOCK_AUTH", "0") == "1":
        return AuthResult(
            error="Chế độ mock đã bị tắt. Chỉ đăng nhập bằng tài khoản Jira thật."
        )

    return _jira_myself(uname, password)


def create_access_token(user: AuthUser) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": user.account_id,
        "name": user.display_name,
        "email": user.email,
        "role": user.role,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> AuthUser | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        account_id = payload.get("sub", "")
        roster = load_roster_employees(live_data_dir())
        emp = next((e for e in roster if e.account_id.lower() == account_id.lower()), None)
        user = AuthUser(
            account_id=account_id,
            display_name=payload.get("name") or account_id,
            email=payload.get("email", ""),
            team=emp.team if emp else None,
            center=emp.center if emp else None,
            role=_role_for_account(account_id),
        )
        return refresh_user_role(user)
    except JWTError:
        return None
