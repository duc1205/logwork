"""Đọc/ghi cấu hình đối soát và ngày nghỉ lễ (fixtures/live)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from ..infra.data_loader import load_config, load_holidays, load_overtime, load_roster_employees
from ..domain.models import OvertimeStatus
from .live_data import live_data_dir

CONFIG_FILE = "config.json"
HOLIDAYS_FILE = "holidays.json"
OVERTIME_FILE = "overtime.json"


def _ot_rules_dict(cfg) -> dict:
    r = cfg.ot_rules
    return {
        "max_ot_hours_per_day": r.max_ot_hours_per_day,
        "max_daily_hours": r.max_daily_hours,
        "ot_grace_hours": r.ot_grace_hours,
        "accept_approved": r.accept_approved,
        "accept_pending": r.accept_pending,
        "allow_weekend_logging": r.allow_weekend_logging,
        "allow_holiday_logging": r.allow_holiday_logging,
        "allow_leave_logging": r.allow_leave_logging,
        "valid_max_formula": "min(min_hours + min(OT, max_ot) + grace, max_daily)",
    }


def _config_path(data_dir: Path | None = None) -> Path:
    return (data_dir or live_data_dir()) / CONFIG_FILE


def _holidays_path(data_dir: Path | None = None) -> Path:
    return (data_dir or live_data_dir()) / HOLIDAYS_FILE


def _read_config_raw(data_dir: Path | None = None) -> dict:
    path = _config_path(data_dir)
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: list | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _overtime_path(data_dir: Path | None = None) -> Path:
    return (data_dir or live_data_dir()) / OVERTIME_FILE


def get_audit_settings(data_dir: Path | None = None) -> dict:
    """Cấu hình đối soát hiện tại (penalty, tolerance, …)."""
    cfg = load_config(data_dir or live_data_dir())
    raw = _read_config_raw(data_dir)
    return {
        "min_hours": cfg.min_hours,
        "max_hours": cfg.max_hours,
        "tolerance_hours": cfg.tolerance_hours,
        "penalty_per_md": int(cfg.penalty_per_md),
        "compensation_threshold": cfg.compensation_threshold,
        "predictive_tue_pace_min": cfg.predictive_tue_pace_min,
        "predictive_wed_pace_min": cfg.predictive_wed_pace_min,
        "ot_rules": _ot_rules_dict(cfg),
        "data_dir": str(data_dir or live_data_dir()),
        "note": raw.get("_note"),
    }


def update_audit_settings(
    *,
    penalty_per_md: int | None = None,
    tolerance_hours: float | None = None,
    compensation_threshold: float | None = None,
    data_dir: Path | None = None,
) -> dict:
    directory = data_dir or live_data_dir()
    raw = _read_config_raw(directory)
    if penalty_per_md is not None:
        if penalty_per_md < 0:
            raise ValueError("penalty_per_md phải >= 0")
        raw["penalty_per_md"] = int(penalty_per_md)
    if tolerance_hours is not None:
        if tolerance_hours < 0:
            raise ValueError("tolerance_hours phải >= 0")
        raw["tolerance_hours"] = float(tolerance_hours)
    if compensation_threshold is not None:
        if compensation_threshold <= 0:
            raise ValueError("compensation_threshold phải > 0")
        raw["compensation_threshold"] = float(compensation_threshold)
    _write_json(_config_path(directory), raw)
    return get_audit_settings(directory)


def update_ot_rules(
    *,
    max_ot_hours_per_day: float | None = None,
    max_daily_hours: float | None = None,
    ot_grace_hours: float | None = None,
    accept_approved: bool | None = None,
    accept_pending: bool | None = None,
    allow_weekend_logging: bool | None = None,
    allow_holiday_logging: bool | None = None,
    allow_leave_logging: bool | None = None,
    data_dir: Path | None = None,
) -> dict:
    directory = data_dir or live_data_dir()
    raw = _read_config_raw(directory)
    block = dict(raw.get("ot_rules") or {})
    if max_ot_hours_per_day is not None:
        if max_ot_hours_per_day < 0:
            raise ValueError("max_ot_hours_per_day phải >= 0")
        block["max_ot_hours_per_day"] = float(max_ot_hours_per_day)
    if max_daily_hours is not None:
        if max_daily_hours <= 0:
            raise ValueError("max_daily_hours phải > 0")
        block["max_daily_hours"] = float(max_daily_hours)
    if ot_grace_hours is not None:
        if ot_grace_hours < 0:
            raise ValueError("ot_grace_hours phải >= 0")
        block["ot_grace_hours"] = float(ot_grace_hours)
    for key, val in (
        ("accept_approved", accept_approved),
        ("accept_pending", accept_pending),
        ("allow_weekend_logging", allow_weekend_logging),
        ("allow_holiday_logging", allow_holiday_logging),
        ("allow_leave_logging", allow_leave_logging),
    ):
        if val is not None:
            block[key] = bool(val)
    if not block.get("accept_approved") and not block.get("accept_pending"):
        raise ValueError("Cần chấp nhận ít nhất một trạng thái OT (approved hoặc pending)")
    raw["ot_rules"] = block
    _write_json(_config_path(directory), raw)
    return _ot_rules_dict(load_config(directory))


def _display_name_map(data_dir: Path | None = None) -> dict[str, str]:
    directory = data_dir or live_data_dir()
    return {
        e.account_id.lower(): e.display_name
        for e in load_roster_employees(directory)
        if e.display_name
    }


def list_overtime(data_dir: Path | None = None) -> list[dict]:
    records = load_overtime(data_dir or live_data_dir())
    records.sort(key=lambda r: (r.ot_date, r.employee_id))
    names = _display_name_map(data_dir)
    return [
        {
            "employee_id": r.employee_id,
            "display_name": names.get(r.employee_id.lower(), r.employee_id),
            "ot_date": r.ot_date.isoformat(),
            "ot_hours": r.ot_hours,
            "reason": r.reason,
            "status": r.status.value,
            "approved_by": r.approved_by,
        }
        for r in records
    ]


def _load_overtime_raw(data_dir: Path) -> list[dict]:
    path = _overtime_path(data_dir)
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def add_overtime_record(
    *,
    employee_id: str,
    ot_date: date,
    ot_hours: float,
    reason: str = "",
    status: str = "approved",
    approved_by: str | None = None,
    data_dir: Path | None = None,
) -> list[dict]:
    eid = employee_id.strip().lower()
    if not eid:
        raise ValueError("employee_id không được để trống")
    if ot_hours <= 0:
        raise ValueError("ot_hours phải > 0")
    try:
        st = OvertimeStatus(status.strip().lower())
    except ValueError as exc:
        raise ValueError("status phải là approved, pending hoặc rejected") from exc
    if st == OvertimeStatus.REJECTED:
        raise ValueError("Không thêm OT rejected — chỉ approved/pending")

    directory = data_dir or live_data_dir()
    items = _load_overtime_raw(directory)
    key = (eid, ot_date.isoformat())
    if any(i.get("employee_id", "").lower() == key[0] and i.get("ot_date") == key[1] for i in items):
        raise ValueError(f"OT {eid} ngày {ot_date} đã tồn tại")

    items.append(
        {
            "employee_id": eid,
            "ot_date": ot_date.isoformat(),
            "ot_hours": float(ot_hours),
            "reason": reason.strip(),
            "status": st.value,
            "approved_by": approved_by,
        }
    )
    items.sort(key=lambda i: (i["ot_date"], i["employee_id"]))
    _write_json(_overtime_path(directory), items)
    return list_overtime(directory)


def remove_overtime_record(
    employee_id: str,
    ot_date: date,
    data_dir: Path | None = None,
) -> list[dict]:
    directory = data_dir or live_data_dir()
    eid = employee_id.strip().lower()
    key = ot_date.isoformat()
    items = _load_overtime_raw(directory)
    filtered = [
        i
        for i in items
        if not (i.get("employee_id", "").lower() == eid and i.get("ot_date") == key)
    ]
    if len(filtered) == len(items):
        raise ValueError(f"Không tìm thấy OT {eid} ngày {key}")
    _write_json(_overtime_path(directory), filtered)
    return list_overtime(directory)


def list_holidays(data_dir: Path | None = None) -> list[dict]:
    holidays = load_holidays(data_dir or live_data_dir())
    holidays.sort(key=lambda h: h.holiday_date)
    return [
        {
            "holiday_date": h.holiday_date.isoformat(),
            "name": h.name,
            "is_company_wide": h.is_company_wide,
        }
        for h in holidays
    ]


def add_holiday(
    *,
    holiday_date: date,
    name: str,
    is_company_wide: bool = True,
    data_dir: Path | None = None,
) -> list[dict]:
    label = name.strip()
    if not label:
        raise ValueError("Tên ngày lễ không được để trống")
    directory = data_dir or live_data_dir()
    items = list_holidays(directory)
    key = holiday_date.isoformat()
    if any(h["holiday_date"] == key for h in items):
        raise ValueError(f"Ngày {key} đã có trong danh sách nghỉ lễ")
    items.append(
        {
            "holiday_date": key,
            "name": label,
            "is_company_wide": is_company_wide,
        }
    )
    items.sort(key=lambda h: h["holiday_date"])
    _write_json(_holidays_path(directory), items)
    return items


def remove_holiday(holiday_date: date, data_dir: Path | None = None) -> list[dict]:
    directory = data_dir or live_data_dir()
    key = holiday_date.isoformat()
    items = [h for h in list_holidays(directory) if h["holiday_date"] != key]
    if len(items) == len(list_holidays(directory)):
        raise ValueError(f"Không tìm thấy ngày nghỉ {key}")
    _write_json(_holidays_path(directory), items)
    return items
