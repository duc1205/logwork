"""FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth_service import AuthUser, decode_token, is_qa_user, is_settings_admin, refresh_user_role
from .credential_store import JiraCredentials, get as get_credentials

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AuthUser:
    if creds is None or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Chưa đăng nhập")
    user = decode_token(creds.credentials)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ hoặc đã hết hạn")
    return refresh_user_role(user)


def get_jira_credentials(
    user: AuthUser = Depends(get_current_user),
) -> JiraCredentials:
    creds = get_credentials(user.account_id)
    if creds is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.",
        )
    return creds


def require_admin(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """QA hoặc admin — xem team, golden, job nhắc."""
    if not is_qa_user(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Cần quyền QA")
    return user


def require_settings_admin(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Chỉ admin (LOGWORK_ADMIN_USERS) — cấu hình phạt, lễ, OT."""
    if not is_settings_admin(user):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Cần quyền cấu hình Logwork (LOGWORK_ADMIN_USERS — không phải Administrator Jira)",
        )
    return user
