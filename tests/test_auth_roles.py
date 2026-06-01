"""Tests phân quyền admin / qa / employee — không liên quan Jira Administrator."""

from __future__ import annotations

from logwork.api import auth_service as auth
from logwork.api.auth_service import AuthUser, is_qa_user, is_settings_admin


def test_role_tiers() -> None:
    old_admin = auth.ADMIN_USERS
    old_qa = auth.QA_USERS
    try:
        auth.ADMIN_USERS = {"cfg_admin"}
        auth.QA_USERS = {"cfg_admin", "qa_only"}

        assert auth._role_for_account("cfg_admin") == "admin"
        assert is_settings_admin(AuthUser("cfg_admin", "cfg_admin", role="admin"))
        assert is_qa_user(AuthUser("cfg_admin", "cfg_admin", role="admin"))

        assert auth._role_for_account("qa_only") == "qa"
        assert is_qa_user(AuthUser("qa_only", "qa_only", role="qa"))
        assert not is_settings_admin(AuthUser("qa_only", "qa_only", role="qa"))

        assert auth._role_for_account("random_employee") == "employee"
        assert not is_qa_user(AuthUser("random_employee", "x", role="employee"))
    finally:
        auth.ADMIN_USERS = old_admin
        auth.QA_USERS = old_qa


def test_refresh_user_role_from_env() -> None:
    old_admin = auth.ADMIN_USERS
    old_qa = auth.QA_USERS
    try:
        auth.ADMIN_USERS = set()
        auth.QA_USERS = {"qa_only"}
        user = AuthUser("qa_only", "QA User", role="employee")
        refreshed = auth.refresh_user_role(user)
        assert refreshed.role == "qa"
    finally:
        auth.ADMIN_USERS = old_admin
        auth.QA_USERS = old_qa


def run_tests() -> None:
    test_role_tiers()
    test_refresh_user_role_from_env()
    print("OK: auth role tests passed")


if __name__ == "__main__":
    run_tests()
