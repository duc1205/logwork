"""Pipeline đối soát — chỉ dữ liệu Jira (ProjectTimesheet + Effort/Holiday)."""

from __future__ import annotations

import logging
import os
from datetime import date

from ..application.pipeline import run_reconciliation
from ..domain.models import Employee, WeeklyReport
from ..domain.period_utils import month_range, parse_month, week_range
from ..infra.data_loader import (
    PeriodData,
    WeekData,
    load_holidays,
    load_overtime,
    load_roster_employees,
)
from ..infra.holiday_plugin_client import HolidayPluginClient, HolidayPluginConfig
from ..infra.timesheet_plugin_client import TimesheetPluginClient, TimesheetPluginConfig
from .auth_service import AuthUser, JIRA_BASE_URL
from .credential_store import JiraCredentials
from .jira_errors import JiraFetchError
from .jira_users import resolve_jira_display_names
from .live_config import load_audit_config
from .live_data import live_data_dir

logger = logging.getLogger("logwork.user_pipeline")

DEFAULT_TARGET_MD_WEEK = 5.0
DEFAULT_TARGET_MD_MONTH = 21.0


def _require_creds(creds: JiraCredentials | None) -> JiraCredentials:
    if creds is None:
        raise JiraFetchError("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại Jira.")
    return creds


def _data_dir():
    return live_data_dir()


def _plugin_config(creds: JiraCredentials) -> TimesheetPluginConfig:
    return TimesheetPluginConfig(
        base_url=JIRA_BASE_URL,
        username=creds.username,
        password=creds.password,
    )


def _holiday_config(creds: JiraCredentials) -> HolidayPluginConfig:
    return HolidayPluginConfig(
        base_url=JIRA_BASE_URL,
        username=creds.username,
        password=creds.password,
    )


def _csv_employee_map() -> dict[str, Employee]:
    return {e.account_id.lower(): e for e in load_roster_employees(_data_dir())}


def _display_name(
    account_id: str,
    *,
    csv_map: dict[str, Employee],
    name_map: dict[str, str],
) -> str:
    aid = account_id.lower()
    jira_name = name_map.get(aid, "").strip()
    if jira_name and jira_name.lower() != aid:
        return jira_name
    csv = csv_map.get(aid)
    if csv and csv.display_name and csv.display_name.lower() != aid:
        return csv.display_name
    return jira_name or aid


def _resolve_name_map(creds: JiraCredentials, account_ids: set[str]) -> dict[str, str]:
    if not account_ids:
        return {}
    try:
        return resolve_jira_display_names(JIRA_BASE_URL, creds, sorted(account_ids))
    except Exception as exc:
        logger.warning("Jira display name lookup failed: %s", exc)
        return {}


def _roster_only() -> bool:
    """Chỉ đối soát roster CSV khi LOGWORK_ROSTER_ONLY=1 và có dòng trong employees.csv."""
    if os.environ.get("LOGWORK_ROSTER_ONLY", "0") != "1":
        return False
    return len(_csv_employee_map()) > 0


def _team_scope() -> tuple[str | None, str | None]:
    team = os.environ.get("LOGWORK_TEAM", "").strip() or None
    center = os.environ.get("LOGWORK_CENTER", "").strip() or None
    return team, center


def _filter_team_employees(employees: list[Employee]) -> list[Employee]:
    team, center = _team_scope()
    if not team and not center:
        return employees
    out: list[Employee] = []
    for e in employees:
        if team and (e.team or "").lower() != team.lower():
            continue
        if center and (e.center or "").lower() != center.lower():
            continue
        out.append(e)
    return out


def _apply_team_scope(employees: list[Employee], entries: list) -> tuple[list[Employee], list]:
    employees = _filter_team_employees(employees)
    allowed = {e.account_id.lower() for e in employees}
    if not allowed:
        return employees, []
    filtered_entries = [e for e in entries if e.employee_id.lower() in allowed]
    return employees, filtered_entries


def _employee_from_account(
    account_id: str,
    user: AuthUser | None = None,
    *,
    name_map: dict[str, str] | None = None,
) -> Employee:
    aid = account_id.lower()
    csv_map = _csv_employee_map()
    csv = csv_map.get(aid)
    names = name_map or {}
    if csv:
        dn = _display_name(aid, csv_map=csv_map, name_map=names)
        return Employee(
            account_id=csv.account_id,
            display_name=dn,
            email=csv.email,
            team=csv.team,
            center=csv.center,
            expected_hours_per_day=csv.expected_hours_per_day,
            target_md_week=csv.target_md_week,
            target_md_month=csv.target_md_month,
        )
    if user and user.account_id.lower() == aid:
        return Employee(
            account_id=user.account_id,
            display_name=user.display_name or aid,
            email=user.email or f"{user.account_id}@tinhvan.vn",
            team=user.team,
            center=user.center,
            expected_hours_per_day=8.0,
            target_md_week=DEFAULT_TARGET_MD_WEEK,
            target_md_month=DEFAULT_TARGET_MD_MONTH,
        )
    dn = _display_name(aid, csv_map=csv_map, name_map=names)
    return Employee(
        account_id=account_id,
        display_name=dn,
        email=f"{account_id}@tinhvan.vn",
        expected_hours_per_day=8.0,
        target_md_week=DEFAULT_TARGET_MD_WEEK,
        target_md_month=DEFAULT_TARGET_MD_MONTH,
    )


def _build_team_employees(
    entries,
    *,
    roster: list[Employee] | None = None,
    creds: JiraCredentials | None = None,
) -> list[Employee]:
    """Gom NV từ worklog Jira + roster CSV (nếu có — để thấy NV chưa log)."""
    csv_map = _csv_employee_map()
    ids: set[str] = {e.employee_id.lower() for e in entries}
    if _roster_only():
        ids = set(csv_map.keys())
        if roster:
            ids.update(e.account_id.lower() for e in roster)
    else:
        if roster:
            ids.update(e.account_id.lower() for e in roster)
        if csv_map:
            ids.update(csv_map.keys())

    name_map = _resolve_name_map(creds, ids) if creds else {}

    employees: list[Employee] = []
    for aid in sorted(ids):
        if aid in csv_map:
            csv = csv_map[aid]
            employees.append(
                Employee(
                    account_id=csv.account_id,
                    display_name=_display_name(aid, csv_map=csv_map, name_map=name_map),
                    email=csv.email,
                    team=csv.team,
                    center=csv.center,
                    expected_hours_per_day=csv.expected_hours_per_day,
                    target_md_week=csv.target_md_week,
                    target_md_month=csv.target_md_month,
                )
            )
        else:
            employees.append(
                Employee(
                    account_id=aid,
                    display_name=_display_name(aid, csv_map=csv_map, name_map=name_map),
                    email=f"{aid}@tinhvan.vn",
                    expected_hours_per_day=8.0,
                    target_md_week=DEFAULT_TARGET_MD_WEEK,
                    target_md_month=DEFAULT_TARGET_MD_MONTH,
                )
            )
    return employees


def _fetch_entries(
    creds: JiraCredentials,
    *,
    start_date: date,
    end_date: date,
    usernames: list[str] | None,
) -> list:
    config = load_audit_config()
    plugin = TimesheetPluginClient(_plugin_config(creds))
    try:
        return plugin.fetch_worklogs(
            start_date=start_date,
            end_date=end_date,
            project_keys=config.project_keys,
            usernames=usernames,
        )
    except Exception as exc:
        logger.exception("ProjectTimesheet fetch failed")
        raise JiraFetchError(
            "Không lấy được worklog từ Jira ProjectTimesheet.",
            detail=str(exc),
        ) from exc


def _fetch_leaves_safe(
    creds: JiraCredentials,
    *,
    employee_id: str,
    start_date: date,
    end_date: date,
) -> list:
    try:
        client = HolidayPluginClient(_holiday_config(creds))
        return client.fetch_leaves(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as exc:
        logger.warning("Holiday plugin skipped for %s: %s", employee_id, exc)
        return []


def load_user_week(
    user: AuthUser,
    creds: JiraCredentials,
    *,
    anchor_date: date | None = None,
    account_id: str | None = None,
) -> WeekData:
    config = load_audit_config()
    anchor = anchor_date or date.today()
    week_start, week_end = week_range(anchor)
    target_account = (account_id or user.account_id).lower()
    name_map = _resolve_name_map(creds, {target_account})
    employee = _employee_from_account(target_account, user, name_map=name_map)

    entries = _fetch_entries(
        creds,
        start_date=week_start,
        end_date=week_end,
        usernames=[target_account],
    )

    leaves = _fetch_leaves_safe(
        creds,
        employee_id=target_account,
        start_date=week_start,
        end_date=week_end,
    )

    return WeekData(
        anchor_date=anchor,
        config=config,
        employees=[employee],
        entries=entries,
        holidays=load_holidays(_data_dir()),
        leaves=leaves,
        overtime=load_overtime(_data_dir()),
        source="plugin",
    )


def load_user_period(
    user: AuthUser,
    creds: JiraCredentials,
    period_start: date,
    period_end: date,
    *,
    account_id: str | None = None,
) -> PeriodData:
    config = load_audit_config()
    target_account = (account_id or user.account_id).lower()
    name_map = _resolve_name_map(creds, {target_account})
    employee = _employee_from_account(target_account, user, name_map=name_map)

    entries = _fetch_entries(
        creds,
        start_date=period_start,
        end_date=period_end,
        usernames=[target_account],
    )
    leaves = _fetch_leaves_safe(
        creds,
        employee_id=target_account,
        start_date=period_start,
        end_date=period_end,
    )

    return PeriodData(
        period_start=period_start,
        period_end=period_end,
        config=config,
        employees=[employee],
        entries=entries,
        holidays=load_holidays(_data_dir()),
        leaves=leaves,
        overtime=load_overtime(_data_dir()),
        source="plugin",
    )


def load_team_week(
    creds: JiraCredentials,
    *,
    anchor_date: date | None = None,
) -> WeekData:
    """QA: lấy toàn bộ worklog tuần từ Jira (không giới hạn employees.csv mock)."""
    config = load_audit_config()
    anchor = anchor_date or date.today()
    week_start, week_end = week_range(anchor)
    roster = load_roster_employees(_data_dir())

    entries = _fetch_entries(
        creds,
        start_date=week_start,
        end_date=week_end,
        usernames=None,
    )
    employees = _build_team_employees(entries, roster=roster, creds=creds)
    employees, entries = _apply_team_scope(employees, entries)

    return WeekData(
        anchor_date=anchor,
        config=config,
        employees=employees,
        entries=entries,
        holidays=load_holidays(_data_dir()),
        leaves=[],
        overtime=load_overtime(_data_dir()),
        source="plugin_team",
    )


def load_team_period(
    creds: JiraCredentials,
    period_start: date,
    period_end: date,
) -> PeriodData:
    config = load_audit_config()
    roster = load_roster_employees(_data_dir())
    entries = _fetch_entries(
        creds,
        start_date=period_start,
        end_date=period_end,
        usernames=None,
    )
    employees = _build_team_employees(entries, roster=roster, creds=creds)
    employees, entries = _apply_team_scope(employees, entries)

    return PeriodData(
        period_start=period_start,
        period_end=period_end,
        config=config,
        employees=employees,
        entries=entries,
        holidays=load_holidays(_data_dir()),
        leaves=[],
        overtime=load_overtime(_data_dir()),
        source="plugin_team",
    )


def _run(data: WeekData) -> tuple[WeeklyReport, str]:
    return run_reconciliation(data), data.source


def _run_period(data: PeriodData, *, monthly: bool = False) -> tuple[WeeklyReport, str]:
    return run_reconciliation(data, monthly=monthly), data.source


def reconcile_for_user(
    user: AuthUser,
    creds: JiraCredentials | None,
    *,
    anchor_date: date | None = None,
    month: str | None = None,
    period_start: date | None = None,
    period_end: date | None = None,
    account_id: str | None = None,
) -> tuple[WeeklyReport, str]:
    creds = _require_creds(creds)

    if month:
        year, mon = parse_month(month)
        ps, pe = month_range(year, mon)
        return _run_period(
            load_user_period(user, creds, ps, pe, account_id=account_id),
            monthly=True,
        )

    if period_start and period_end:
        return _run_period(
            load_user_period(
                user, creds, period_start, period_end, account_id=account_id,
            ),
        )

    anchor = period_start if period_start else anchor_date
    return _run(load_user_week(user, creds, anchor_date=anchor, account_id=account_id))


def reconcile_for_team(
    creds: JiraCredentials,
    *,
    anchor_date: date | None = None,
    month: str | None = None,
    period_start: date | None = None,
    period_end: date | None = None,
) -> tuple[WeeklyReport, str]:
    creds = _require_creds(creds)

    if month:
        year, mon = parse_month(month)
        ps, pe = month_range(year, mon)
        return _run_period(load_team_period(creds, ps, pe), monthly=True)

    if period_start and period_end:
        return _run_period(load_team_period(creds, period_start, period_end))

    anchor = period_start if period_start else anchor_date
    return _run(load_team_week(creds, anchor_date=anchor))


def list_jira_accounts(creds: JiraCredentials) -> list[dict[str, str]]:
    """Danh sách username Jira (plugin) — fallback roster CSV khi plugin lỗi."""
    creds = _require_creds(creds)
    csv_map = _csv_employee_map()

    def _from_roster() -> list[dict[str, str]]:
        if not csv_map:
            return []
        return [
            {
                "account_id": emp.account_id,
                "display_name": emp.display_name,
                "jira_user_id": "",
                "source": "roster",
            }
            for _, emp in sorted(csv_map.items(), key=lambda x: x[0])
        ]

    plugin = TimesheetPluginClient(_plugin_config(creds))
    try:
        users = plugin.fetch_all_users()
    except Exception as exc:
        logger.warning("Jira user list failed — fallback roster: %s", exc)
        roster = _from_roster()
        if roster:
            return roster
        raise JiraFetchError("Không tải được danh sách user Jira.", detail=str(exc)) from exc

    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for u in sorted(users, key=lambda x: x.username.lower()):
        aid = u.username.lower()
        seen.add(aid)
        csv = csv_map.get(aid)
        display = csv.display_name if csv and csv.display_name.lower() != aid else u.username
        out.append(
            {
                "account_id": u.username,
                "display_name": display,
                "jira_user_id": str(u.id),
                "source": "jira",
            }
        )
    for aid, emp in sorted(csv_map.items(), key=lambda x: x[0]):
        if aid in seen:
            continue
        out.append(
            {
                "account_id": emp.account_id,
                "display_name": emp.display_name,
                "jira_user_id": "",
                "source": "roster",
            }
        )
    out.sort(key=lambda x: x["account_id"].lower())
    return out
