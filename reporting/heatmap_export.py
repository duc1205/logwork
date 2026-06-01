"""Export dữ liệu heatmap (JSON cho UI demo)."""

from __future__ import annotations

import json
from pathlib import Path

from ..domain.models import WeeklyReport


def _cell_status(audit, *, has_compensation: bool) -> tuple[str, str]:
    if audit.is_holiday or audit.is_leave:
        return "off", "gray"
    if has_compensation and audit.missed_hours > 0:
        return "compensation", "purple"
    if audit.required_hours <= 0:
        return "off", "gray"
    h = audit.actual_hours
    if h >= audit.required_hours - 0.25:
        return "ok", "green"
    if h >= 6:
        return "near", "lightgreen"
    if h >= 4:
        return "low", "yellow"
    if h > 0:
        return "bad", "orange"
    return "missing", "red"


def _period_label(report: WeeklyReport) -> str:
    span = (report.week_end - report.week_start).days + 1
    if span > 7:
        return report.week_start.strftime("%Y-%m")
    return report.week_start.isoformat()


def build_heatmap_payload(report: WeeklyReport) -> dict:
    """Payload JSON heatmap — dùng cho export file và API."""
    comp_days: set[tuple[str, str]] = set()
    for s in report.summaries:
        for p in s.compensation_pairs:
            comp_days.add((s.employee_id, p.under_day.isoformat()))
            comp_days.add((s.employee_id, p.over_day.isoformat()))

    cells = []
    for summary in report.summaries:
        for audit in summary.daily_audits:
            has_comp = (summary.employee_id, audit.work_date.isoformat()) in comp_days
            status, color = _cell_status(audit, has_compensation=has_comp)
            cells.append(
                {
                    "employee_id": summary.employee_id,
                    "display_name": summary.display_name,
                    "date": audit.work_date.isoformat(),
                    "actual": audit.actual_hours,
                    "required": audit.required_hours,
                    "status": status,
                    "color": color,
                    "penalty": audit.penalty,
                    "is_leave": audit.is_leave,
                    "is_holiday": audit.is_holiday,
                }
            )

    return {
        "week_start": report.week_start.isoformat(),
        "week_end": report.week_end.isoformat(),
        "cells": cells,
    }


def export_heatmap_json(report: WeeklyReport, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"heatmap_{_period_label(report)}.json"
    payload = build_heatmap_payload(report)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
