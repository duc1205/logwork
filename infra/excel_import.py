"""Import Timesheet / Leave / Employee từ CSV (format export Jira / HR)."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from ..domain.models import Employee, EmployeeLeave, LeaveType, OvertimeRecord, OvertimeStatus, TimesheetEntry

# Map tên cột thường gặp (Jira Timesheet export) → field nội bộ
TIMESHEET_COLUMN_ALIASES: dict[str, str] = {
    "user": "employee_id",
    "author": "employee_id",
    "account": "employee_id",
    "username": "employee_id",
    "employee_id": "employee_id",
    "work date": "work_date",
    "started": "work_date",
    "start date": "work_date",
    "date": "work_date",
    "time spent": "hours",
    "hours": "hours",
    "time spent (h)": "hours",
    "logged": "hours",
    "issue key": "issue_key",
    "issue": "issue_key",
    "project": "project_key",
    "project key": "project_key",
}

LEAVE_COLUMN_ALIASES: dict[str, str] = {
    "account": "employee_id",
    "employee_id": "employee_id",
    "user": "employee_id",
    "date": "leave_date",
    "leave date": "leave_date",
    "type": "leave_type",
}

EMPLOYEE_COLUMN_ALIASES: dict[str, str] = {
    "account": "account_id",
    "account_id": "account_id",
    "username": "account_id",
    "full name": "display_name",
    "name": "display_name",
    "display_name": "display_name",
    "email": "email",
    "team": "team",
    "center": "center",
    "trung tam": "center",
    "target_md_week": "target_md_week",
    "target": "target_md_week",
    "target (md)": "target_md_month",
    "target_md_month": "target_md_month",
}

OT_COLUMN_ALIASES: dict[str, str] = {
    "account": "employee_id",
    "employee_id": "employee_id",
    "user": "employee_id",
    "date": "ot_date",
    "ot date": "ot_date",
    "ot hours": "ot_hours",
    "hours": "ot_hours",
    "status": "status",
    "reason": "reason",
    "approved by": "approved_by",
}


def _normalize_header(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _map_row(headers: list[str], aliases: dict[str, str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for h in headers:
        key = aliases.get(_normalize_header(h))
        if key:
            mapping[key] = h
    return mapping


def _parse_date(value: str) -> date:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    # Jira datetime: 2026-05-18T09:00:00.000+0700
    if "T" in value:
        return date.fromisoformat(value.split("T")[0])
    raise ValueError(f"Khong parse duoc ngay: {value!r}")


def _parse_hours(value: str) -> float:
    value = value.strip().replace(",", ".")
    if not value:
        return 0.0
    # "4h 30m" hoặc "4.5"
    h_match = re.match(r"^(\d+(?:\.\d+)?)\s*h?", value, re.I)
    if h_match and "m" not in value.lower():
        return float(h_match.group(1))
    m = re.match(r"^(\d+)h\s*(\d+)m$", value, re.I)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60
    return float(value)


def import_timesheet_csv(
    path: Path,
    *,
    project_keys: tuple[str, ...] = (),
) -> list[TimesheetEntry]:
    """Đọc CSV Timesheet Jira, gộp theo (employee_id, work_date)."""
    raw_rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"CSV trong: {path}")
        col_map = _map_row(list(reader.fieldnames), TIMESHEET_COLUMN_ALIASES)
        required = {"employee_id", "work_date", "hours"}
        missing = required - set(col_map)
        if missing:
            raise ValueError(f"Thieu cot {missing} trong {path.name}. Co: {reader.fieldnames}")

        for row in reader:
            raw_rows.append(row)

    totals: dict[tuple[str, date], float] = defaultdict(float)
    meta: dict[tuple[str, date], dict] = {}

    for row in raw_rows:
        eid = row[col_map["employee_id"]].strip()
        work_date = _parse_date(row[col_map["work_date"]])
        hours = _parse_hours(row[col_map["hours"]])
        issue_key = row.get(col_map.get("issue_key", ""), "").strip() or None
        project_key = row.get(col_map.get("project_key", ""), "").strip() or None

        if project_keys and project_key and project_key not in project_keys:
            continue

        key = (eid, work_date)
        totals[key] += hours
        if key not in meta:
            meta[key] = {"issue_key": issue_key, "project_key": project_key}

    return [
        TimesheetEntry(
            employee_id=eid,
            work_date=day,
            hours=hours,
            issue_key=meta[(eid, day)].get("issue_key"),
            project_key=meta[(eid, day)].get("project_key"),
        )
        for (eid, day), hours in sorted(totals.items())
    ]


def import_leaves_csv(path: Path) -> list[EmployeeLeave]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        col_map = _map_row(list(reader.fieldnames), LEAVE_COLUMN_ALIASES)
        leaves: list[EmployeeLeave] = []
        for row in reader:
            eid = row[col_map["employee_id"]].strip()
            leave_date = _parse_date(row[col_map["leave_date"]])
            lt_raw = row.get(col_map.get("leave_type", ""), "annual").strip().lower()
            try:
                leave_type = LeaveType(lt_raw)
            except ValueError:
                leave_type = LeaveType.OTHER
            leaves.append(
                EmployeeLeave(
                    employee_id=eid,
                    leave_date=leave_date,
                    leave_type=leave_type,
                    source="excel",
                )
            )
        return leaves


def import_employees_csv(path: Path) -> list[Employee]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        col_map = _map_row(list(reader.fieldnames), EMPLOYEE_COLUMN_ALIASES)
        required = {"account_id", "display_name", "email"}
        missing = required - set(col_map)
        if missing:
            raise ValueError(f"Thieu cot {missing} trong {path.name}")

        employees: list[Employee] = []
        for row in reader:
            target_week = row.get(col_map.get("target_md_week", ""), "").strip()
            target_month = row.get(col_map.get("target_md_month", ""), "").strip()
            employees.append(
                Employee(
                    account_id=row[col_map["account_id"]].strip(),
                    display_name=row[col_map["display_name"]].strip(),
                    email=row[col_map["email"]].strip(),
                    team=row.get(col_map.get("team", ""), "").strip() or None,
                    center=row.get(col_map.get("center", ""), "").strip() or None,
                    target_md_week=float(target_week) if target_week else None,
                    target_md_month=float(target_month) if target_month else None,
                )
            )
        return employees


def import_overtime_csv(path: Path) -> list[OvertimeRecord]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        col_map = _map_row(list(reader.fieldnames), OT_COLUMN_ALIASES)
        required = {"employee_id", "ot_date", "ot_hours"}
        missing = required - set(col_map)
        if missing:
            raise ValueError(f"Thieu cot {missing} trong {path.name}")

        records: list[OvertimeRecord] = []
        for row in reader:
            status_raw = row.get(col_map.get("status", ""), "approved").strip().lower()
            try:
                status = OvertimeStatus(status_raw)
            except ValueError:
                status = OvertimeStatus.PENDING
            records.append(
                OvertimeRecord(
                    employee_id=row[col_map["employee_id"]].strip(),
                    ot_date=_parse_date(row[col_map["ot_date"]]),
                    ot_hours=_parse_hours(row[col_map["ot_hours"]]),
                    reason=row.get(col_map.get("reason", ""), "").strip(),
                    status=status,
                    approved_by=row.get(col_map.get("approved_by", ""), "").strip() or None,
                )
            )
        return records


def preview_csv(path: Path) -> dict:
    """Preview nhanh: số dòng, cột map được, mẫu 3 dòng."""
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        rows = [row for i, row in enumerate(reader) if i < 3]
    kind = "timesheet"
    if "email" in {_normalize_header(h) for h in headers}:
        kind = "employees"
    elif "leave date" in {_normalize_header(h) for h in headers} or (
        "date" in {_normalize_header(h) for h in headers}
        and "time spent" not in {_normalize_header(h) for h in headers}
    ):
        kind = "leaves"
    return {"file": path.name, "kind": kind, "headers": headers, "sample_rows": rows}
