"""Fetch báo cáo đối soát theo kỳ — dùng chung cho dashboard routes."""

from __future__ import annotations

from datetime import date

from ..domain.models import WeeklyReport
from .auth_service import AuthUser, is_qa_user
from .credential_store import JiraCredentials
from .period_helpers import effective_as_of_range
from .period_query import ResolvedPeriod
from .user_pipeline import reconcile_for_team, reconcile_for_user


def fetch_user_report(
    user: AuthUser,
    creds: JiraCredentials | None,
    period: ResolvedPeriod,
    *,
    account_id: str | None = None,
) -> tuple[WeeklyReport, str, date]:
    as_of = effective_as_of_range(period.start, period.end)
    target = account_id if is_qa_user(user) and account_id else None

    if period.mode == "month":
        ym = f"{period.start.year:04d}-{period.start.month:02d}"
        report, source = reconcile_for_user(
            user, creds, month=ym, account_id=target,
        )
    else:
        report, source = reconcile_for_user(
            user,
            creds,
            anchor_date=period.anchor,
            period_start=period.start,
            period_end=period.end,
            account_id=target,
        )
    return report, source, as_of


def fetch_team_report(
    creds: JiraCredentials,
    period: ResolvedPeriod,
) -> tuple[WeeklyReport, str, date]:
    as_of = effective_as_of_range(period.start, period.end)
    if period.mode == "month":
        ym = f"{period.start.year:04d}-{period.start.month:02d}"
        report, source = reconcile_for_team(creds, month=ym)
    else:
        report, source = reconcile_for_team(
            creds,
            anchor_date=period.anchor,
            period_start=period.start,
            period_end=period.end,
        )
    return report, source, as_of
