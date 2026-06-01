"""Auth routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth_service import AuthUser, authenticate, create_access_token
from ..credential_store import save as save_credentials
from ..deps import get_current_user
from ..schemas import LoginRequest, TokenResponse, UserInfo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest) -> TokenResponse:
    result = authenticate(body.username, body.password)
    if result.user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=result.error or "Đăng nhập thất bại",
        )
    user = result.user
    save_credentials(user.account_id, body.username.strip(), body.password)
    token = create_access_token(user)
    return TokenResponse(
        access_token=token,
        user=UserInfo(
            account_id=user.account_id,
            display_name=user.display_name,
            email=user.email,
            team=user.team,
            center=user.center,
            role=user.role,
        ),
    )


@router.get("/me", response_model=UserInfo)
def me(user: AuthUser = Depends(get_current_user)) -> UserInfo:
    return UserInfo(
        account_id=user.account_id,
        display_name=user.display_name,
        email=user.email,
        team=user.team,
        center=user.center,
        role=user.role,
    )
