"""Dedup ngày nghỉ cross-source (Jira + Excel)."""

from __future__ import annotations

from ..domain.models import EmployeeLeave


def dedup_leaves(leaves: list[EmployeeLeave]) -> tuple[list[EmployeeLeave], list[tuple[EmployeeLeave, EmployeeLeave]]]:
    """
    Khóa (employee_id, leave_date). Ưu tiên source=jira.
    Trả về leaves đã dedup + cặp trùng phát hiện.
    """
    by_key: dict[tuple[str, str], EmployeeLeave] = {}
    duplicates: list[tuple[EmployeeLeave, EmployeeLeave]] = []

    priority = {"jira": 2, "excel": 1}

    for lv in leaves:
        key = (lv.employee_id, lv.leave_date.isoformat())
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = lv
            continue
        duplicates.append((existing, lv))
        if priority.get(lv.source, 0) >= priority.get(existing.source, 0):
            by_key[key] = lv

    return list(by_key.values()), duplicates
