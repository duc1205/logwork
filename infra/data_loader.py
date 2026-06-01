"""Load dữ liệu từ fixtures/mock hoặc thư mục CSV tùy chỉnh."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .dedup import dedup_leaves
from .excel_import import import_employees_csv, import_leaves_csv, import_timesheet_csv
from .jira_client import create_jira_client
from ..domain.models import (
    AuditConfig,
    Employee,
    EmployeeLeave,
    Holiday,
    LeaveType,
    OtRules,
    OvertimeRecord,
    OvertimeStatus,
    TimesheetEntry,
)
from ..paths import MOCK_DIR
from ..domain.period_utils import month_range, week_range

@dataclass
class PeriodData:
    period_start: date
    period_end: date
    config: AuditConfig
    employees: list[Employee]
    entries: list[TimesheetEntry]
    holidays: list[Holiday]
    leaves: list[EmployeeLeave]
    overtime: list[OvertimeRecord]
    source: str = "mock"  # mock | jira | plugin


@dataclass
class WeekData:
    anchor_date: date
    config: AuditConfig
    employees: list[Employee]
    entries: list[TimesheetEntry]
    holidays: list[Holiday]
    leaves: list[EmployeeLeave]
    overtime: list[OvertimeRecord]
    source: str = "mock"


def _read_json(data_dir: Path, name: str) -> list | dict:
    return json.loads((data_dir / name).read_text(encoding="utf-8"))


def _parse_ot_rules(raw: dict) -> OtRules:
    block = raw.get("ot_rules") or {}
    return OtRules(
        max_ot_hours_per_day=float(block.get("max_ot_hours_per_day", 4.0)),
        max_daily_hours=float(block.get("max_daily_hours", 12.0)),
        ot_grace_hours=float(block.get("ot_grace_hours", 0.0)),
        accept_approved=bool(block.get("accept_approved", True)),
        accept_pending=bool(block.get("accept_pending", False)),
        allow_weekend_logging=bool(block.get("allow_weekend_logging", False)),
        allow_holiday_logging=bool(block.get("allow_holiday_logging", False)),
        allow_leave_logging=bool(block.get("allow_leave_logging", False)),
    )


def load_config(data_dir: Path | None = None) -> AuditConfig:
    raw = _read_json(data_dir or MOCK_DIR, "config.json")
    return AuditConfig(
        min_hours=raw.get("min_hours", 8.0),
        max_hours=raw.get("max_hours", 8.0),
        tolerance_hours=raw.get("tolerance_hours", 0.25),
        penalty_per_md=raw.get("penalty_per_md", 20_000),
        compensation_threshold=raw.get("compensation_threshold", 2.0),
        project_keys=tuple(raw.get("project_keys", [])),
        predictive_tue_pace_min=raw.get("predictive_tue_pace_min", 0.20),
        predictive_wed_pace_min=raw.get("predictive_wed_pace_min", 0.40),
        ot_rules=_parse_ot_rules(raw),
    )


def load_roster_employees(data_dir: Path | None = None) -> list[Employee]:
    """Chỉ roster CSV — không fallback employees.json (API live / QA)."""
    directory = data_dir or MOCK_DIR
    csv_path = directory / "employees.csv"
    if csv_path.is_file():
        return import_employees_csv(csv_path)
    return []


def load_employees(data_dir: Path | None = None) -> list[Employee]:
    """CLI/tests: CSV trước, fallback employees.json khi CSV trống."""
    rows = load_roster_employees(data_dir)
    if rows:
        return rows

    directory = data_dir or MOCK_DIR
    return [
        Employee(
            account_id=e["account_id"],
            display_name=e["display_name"],
            email=e["email"],
            team=e.get("team"),
            center=e.get("center"),
            expected_hours_per_day=e.get("expected_hours_per_day", 8.0),
            target_md_week=e.get("target_md_week"),
            target_md_month=e.get("target_md_month"),
        )
        for e in _read_json(directory, "employees.json")
    ]


def load_timesheet_for_period(
    data_dir: Path,
    *,
    period_start: date,
    period_end: date,
    project_keys: tuple[str, ...] = (),
    use_live_jira: bool = False,
    use_plugin: bool = False,
    employee_usernames: list[str] | None = None,
) -> list[TimesheetEntry]:
    if use_plugin:
        from .timesheet_plugin_client import create_plugin_client

        plugin = create_plugin_client()
        return plugin.fetch_worklogs(
            start_date=period_start,
            end_date=period_end,
            project_keys=project_keys,
            usernames=employee_usernames,
        )
    client = create_jira_client(mock=not use_live_jira, data_dir=data_dir)
    return client.fetch_worklogs(
        start_date=period_start,
        end_date=period_end,
        project_keys=project_keys,
    )


def load_timesheet(
    data_dir: Path | None = None,
    *,
    project_keys: tuple[str, ...] = (),
    week_start: date | None = None,
    week_end: date | None = None,
    use_live_jira: bool = False,
) -> list[TimesheetEntry]:
    directory = data_dir or MOCK_DIR

    if week_start and week_end:
        return load_timesheet_for_period(
            directory,
            period_start=week_start,
            period_end=week_end,
            project_keys=project_keys,
            use_live_jira=use_live_jira,
        )

    csv_path = directory / "jira_timesheet.csv"
    if csv_path.is_file():
        return import_timesheet_csv(csv_path, project_keys=project_keys)

    entries: list[TimesheetEntry] = []
    for row in _read_json(directory, "timesheet.json"):
        pk = row.get("project_key")
        if project_keys and pk and pk not in project_keys:
            continue
        entries.append(
            TimesheetEntry(
                employee_id=row["employee_id"],
                work_date=date.fromisoformat(row["work_date"]),
                hours=float(row["hours"]),
                issue_key=row.get("issue_key"),
                project_key=pk,
            )
        )
    return entries


def load_holidays(data_dir: Path | None = None) -> list[Holiday]:
    return [
        Holiday(
            holiday_date=date.fromisoformat(h["holiday_date"]),
            name=h["name"],
            is_company_wide=h.get("is_company_wide", True),
        )
        for h in _read_json(data_dir or MOCK_DIR, "holidays.json")
    ]


def load_leaves(data_dir: Path | None = None) -> list[EmployeeLeave]:
    directory = data_dir or MOCK_DIR
    leaves: list[EmployeeLeave] = []

    csv_path = directory / "leaves.csv"
    if csv_path.is_file():
        leaves.extend(import_leaves_csv(csv_path))

    json_path = directory / "leaves.json"
    if json_path.is_file():
        leaves.extend(
            EmployeeLeave(
                employee_id=lv["employee_id"],
                leave_date=date.fromisoformat(lv["leave_date"]),
                leave_type=LeaveType(lv.get("leave_type", "annual")),
                source=lv.get("source", "excel"),
            )
            for lv in _read_json(directory, "leaves.json")
        )

    if not leaves:
        return []
    return dedup_leaves(leaves)[0]


def load_overtime(data_dir: Path | None = None) -> list[OvertimeRecord]:
    directory = data_dir or MOCK_DIR
    records: list[OvertimeRecord] = []

    csv_path = directory / "overtime.csv"
    if csv_path.is_file():
        from .excel_import import import_overtime_csv

        records.extend(import_overtime_csv(csv_path))

    json_path = directory / "overtime.json"
    if json_path.is_file():
        records.extend(
            OvertimeRecord(
                employee_id=ot["employee_id"],
                ot_date=date.fromisoformat(ot["ot_date"]),
                ot_hours=float(ot["ot_hours"]),
                reason=ot.get("reason", ""),
                status=OvertimeStatus(ot.get("status", "pending")),
                approved_by=ot.get("approved_by"),
            )
            for ot in _read_json(directory, "overtime.json")
        )
    return records


def _load_period_data(
    period_start: date,
    period_end: date,
    data_dir: Path,
    anchor: date,
    *,
    use_live_jira: bool = False,
    use_plugin: bool = False,
    employee_usernames: list[str] | None = None,
) -> PeriodData:
    config = load_config(data_dir)
    employees = load_employees(data_dir)
    source = "plugin" if use_plugin else ("jira" if use_live_jira else "mock")
    un_list = employee_usernames or ([e.account_id for e in employees] if use_plugin else None)
    return PeriodData(
        period_start=period_start,
        period_end=period_end,
        config=config,
        employees=employees,
        entries=load_timesheet_for_period(
            data_dir,
            period_start=period_start,
            period_end=period_end,
            project_keys=config.project_keys,
            use_live_jira=use_live_jira,
            use_plugin=use_plugin,
            employee_usernames=un_list,
        ),
        holidays=load_holidays(data_dir),
        leaves=load_leaves(data_dir),
        overtime=load_overtime(data_dir),
        source=source,
    )


def load_week(
    anchor_date: date | None = None,
    data_dir: Path | None = None,
    *,
    use_live_jira: bool = False,
    use_plugin: bool = False,
) -> WeekData:
    directory = data_dir or MOCK_DIR
    config = load_config(directory)
    anchor = anchor_date or date.fromisoformat(
        _read_json(directory, "config.json")["anchor_date"]
    )
    week_start, week_end = week_range(anchor)
    period = _load_period_data(
        week_start, week_end, directory, anchor,
        use_live_jira=use_live_jira,
        use_plugin=use_plugin,
    )

    return WeekData(
        anchor_date=anchor,
        config=period.config,
        employees=period.employees,
        entries=period.entries,
        holidays=period.holidays,
        leaves=period.leaves,
        overtime=period.overtime,
        source=period.source,
    )


def load_month(
    year: int,
    month: int,
    data_dir: Path | None = None,
    *,
    use_live_jira: bool = False,
    use_plugin: bool = False,
) -> PeriodData:
    directory = data_dir or MOCK_DIR
    period_start, period_end = month_range(year, month)
    return _load_period_data(
        period_start, period_end, directory, period_start,
        use_live_jira=use_live_jira,
        use_plugin=use_plugin,
    )


def load_mock_week(anchor_date: date | None = None) -> WeekData:
    """Alias giữ tương thích."""
    return load_week(anchor_date)
