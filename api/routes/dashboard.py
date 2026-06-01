"""Dashboard / weekly summary routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from ..auth_service import AuthUser, is_qa_user
from ..credential_store import JiraCredentials
from ..deps import get_current_user, get_jira_credentials, require_admin, require_settings_admin
from ...reporting.report_export import (
    _report_label,
    report_compensation_csv_text,
    report_summary_csv_text,
)
from ..period_helpers import clip_report, heatmap_from_report, summary_from_report
from ..period_query import resolve_period
from ..predictive_helpers import predictive_items
from ..report_fetch import fetch_team_report, fetch_user_report
from ..schemas import HeatmapResponse, PredictiveResponse, WeeklySummaryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _empty_summary(
    report,
    user: AuthUser,
    as_of: date,
    *,
    data_source: str,
    period_mode: str,
) -> WeeklySummaryResponse:
    note = (
        "Không có logwork trong tháng này trên Jira."
        if period_mode == "month"
        else "Không có logwork trong tuần này trên Jira."
    )
    return WeeklySummaryResponse(
        week_start=report.week_start,
        week_end=report.week_end,
        as_of=as_of,
        data_source=data_source,
        period_mode=period_mode,
        display_name=user.display_name,
        account_id=user.account_id,
        holiday_count=0,
        actual_hours=0.0,
        required_hours=0.0,
        missed_hours=0.0,
        penalty=0,
        target_md=0.0,
        note=note,
        daily_audits=[],
        compensation_pairs=[],
    )


@router.get("/summary", response_model=WeeklySummaryResponse)
def weekly_summary(
    week: date | None = Query(None, description="Ngày bất kỳ trong tuần (legacy)"),
    month: str | None = Query(None, description="Tháng YYYY-MM"),
    start: date | None = Query(None, description="Từ ngày (tuần)"),
    end: date | None = Query(None, description="Đến ngày (tuần)"),
    account: str | None = Query(None, description="QA: xem chi tiết NV theo account Jira"),
    user: AuthUser = Depends(get_current_user),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> WeeklySummaryResponse:
    if account and not is_qa_user(user):
        from fastapi import HTTPException

        raise HTTPException(403, detail="Chỉ QA mới xem được account khác")

    period = resolve_period(week=week, month=month, start=start, end=end)
    report, source, as_of = fetch_user_report(
        user, creds, period, account_id=account,
    )

    lookup = (account or user.account_id).lower()
    summary = summary_from_report(report, lookup, as_of, data_source=source)
    if summary:
        return summary.model_copy(update={"period_mode": period.mode})
    empty_user = user
    if account:
        from ..auth_service import AuthUser as AU

        empty_user = AU(
            account_id=account,
            display_name=account,
            email=user.email,
            team=user.team,
            center=user.center,
            role=user.role,
        )
    return _empty_summary(
        report, empty_user, as_of, data_source=source, period_mode=period.mode,
    )


@router.get("/employees")
def jira_employees(
    q: str | None = Query(None, description="Lọc account / tên"),
    _user: AuthUser = Depends(require_settings_admin),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> dict:
    """Admin cấu hình: danh sách account Jira (+ roster)."""
    from ..user_pipeline import list_jira_accounts

    items = list_jira_accounts(creds)
    if q and q.strip():
        needle = q.strip().lower()
        items = [
            i
            for i in items
            if needle in i["account_id"].lower() or needle in i["display_name"].lower()
        ]
    return {"total": len(items), "items": items}


@router.get("/export/summary")
def export_summary_csv(
    week: date | None = Query(None),
    month: str | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
    user: AuthUser = Depends(get_current_user),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> Response:
    """QA: tải CSV summary (format golden) từ Jira live."""
    period = resolve_period(week=week, month=month, start=start, end=end)
    if is_qa_user(user):
        report, _source, as_of = fetch_team_report(creds, period)
    else:
        report, _source, as_of = fetch_user_report(user, creds, period)
    report = clip_report(report, as_of)
    label = _report_label(report)
    filename = f"logwork_{label}_summary.csv"
    return Response(
        content=report_summary_csv_text(report).encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/compensation")
def export_compensation_csv(
    week: date | None = Query(None),
    month: str | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
    user: AuthUser = Depends(get_current_user),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> Response:
    period = resolve_period(week=week, month=month, start=start, end=end)
    if is_qa_user(user):
        report, _source, as_of = fetch_team_report(creds, period)
    else:
        report, _source, as_of = fetch_user_report(user, creds, period)
    report = clip_report(report, as_of)
    label = _report_label(report)
    filename = f"logwork_{label}_compensation.csv"
    return Response(
        content=report_compensation_csv_text(report).encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/summaries", response_model=list[WeeklySummaryResponse])
def all_summaries(
    week: date | None = Query(None),
    month: str | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
    _user: AuthUser = Depends(require_admin),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> list[WeeklySummaryResponse]:
    period = resolve_period(week=week, month=month, start=start, end=end)
    report, source, as_of = fetch_team_report(creds, period)

    out: list[WeeklySummaryResponse] = []
    for s in report.summaries:
        item = summary_from_report(report, s.employee_id, as_of, data_source=source)
        if item:
            out.append(item.model_copy(update={"period_mode": period.mode}))
    return out


@router.get("/heatmap", response_model=HeatmapResponse)
def heatmap(
    week: date | None = Query(None),
    month: str | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
    user: AuthUser = Depends(get_current_user),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> HeatmapResponse:
    period = resolve_period(week=week, month=month, start=start, end=end)
    if is_qa_user(user):
        report, source, as_of = fetch_team_report(creds, period)
        return heatmap_from_report(
            report,
            as_of,
            data_source=source,
            period_mode=period.mode,
            admin=True,
        )
    report, source, as_of = fetch_user_report(user, creds, period)
    return heatmap_from_report(
        report,
        as_of,
        data_source=source,
        period_mode=period.mode,
        account_id=user.account_id,
        admin=False,
    )


@router.get("/predictive", response_model=PredictiveResponse)
def predictive_alerts(
    week: date | None = Query(None),
    month: str | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
    user: AuthUser = Depends(get_current_user),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> PredictiveResponse:
    period = resolve_period(week=week, month=month, start=start, end=end)
    hint = ""
    if period.mode == "month":
        from ..period_helpers import effective_as_of_range

        as_of = effective_as_of_range(period.start, period.end)
        return PredictiveResponse(
            week_start=period.start,
            week_end=period.end,
            as_of=as_of,
            period_mode="month",
            total=0,
            items=[],
            hint="Cảnh báo predictive chỉ áp dụng cho tuần (T2–T3 pace).",
        )

    if is_qa_user(user):
        report, source, as_of = fetch_team_report(creds, period)
        items = predictive_items(report, as_of, admin=True)
    else:
        report, source, as_of = fetch_user_report(user, creds, period)
        items = predictive_items(report, as_of, account_id=user.account_id, admin=False)

    day_index = (as_of - report.week_start).days
    if day_index not in (0, 1):
        hint = "Ngưỡng pace chỉ kiểm tra chiều thứ Ba và thứ Tư."

    return PredictiveResponse(
        week_start=report.week_start,
        week_end=report.week_end,
        as_of=as_of,
        period_mode=period.mode,
        data_source=source,
        total=len(items),
        items=items,
        hint=hint,
    )


@router.get("/week-info")
def week_info(
    week: date | None = Query(None),
    month: str | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
) -> dict:
    from ..period_helpers import effective_as_of_range

    period = resolve_period(week=week, month=month, start=start, end=end)
    return {
        "period_mode": period.mode,
        "week_start": period.start.isoformat(),
        "week_end": period.end.isoformat(),
        "as_of": effective_as_of_range(period.start, period.end).isoformat(),
    }
