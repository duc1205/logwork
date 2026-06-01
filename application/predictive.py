"""Predictive warning — pace giữa tuần + pattern cá nhân (không dùng ML)."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ..domain.models import AuditConfig, EmployeeWeeklySummary, WeeklyReport

HISTORY_FILE = "log_history.json"


@dataclass
class PredictiveAlert:
    employee_id: str
    display_name: str
    alert_type: str  # midweek_pace | pattern
    message: str


def _pace_threshold(weekday: int, config: AuditConfig) -> float:
    """T2=0.20, T3=0.40 theo SRS (cấu hình trong config)."""
    if weekday == 0:
        return config.predictive_tue_pace_min
    if weekday == 1:
        return config.predictive_wed_pace_min
    return 0.0


def midweek_pace_alerts(
    report: WeeklyReport,
    *,
    as_of: date,
    config: AuditConfig,
) -> list[PredictiveAlert]:
    """Cảnh báo khi pace tuần thấp hơn ngưỡng (chiều T2/T3)."""
    if as_of < report.week_start or as_of > report.week_end:
        return []

    day_index = (as_of - report.week_start).days
    threshold = _pace_threshold(day_index, config)
    if threshold <= 0:
        return []

    alerts: list[PredictiveAlert] = []
    remaining_work_days = len([d for d in report.working_days if d > as_of])

    for summary in report.summaries:
        required_total = summary.required_hours
        if required_total <= 0:
            continue

        logged_to_date = sum(
            a.actual_hours for a in summary.daily_audits if a.work_date <= as_of
        )
        pace = logged_to_date / required_total
        if pace >= threshold:
            continue

        needed = required_total - logged_to_date
        per_day = needed / remaining_work_days if remaining_work_days else needed
        alerts.append(
            PredictiveAlert(
                employee_id=summary.employee_id,
                display_name=summary.display_name,
                alert_type="midweek_pace",
                message=(
                    f"Chieu {as_of.strftime('%A')}: ban moi log {logged_to_date:.0f}/"
                    f"{required_total:.0f}h tuan nay. Can ~{per_day:.0f}h/ngay con lai "
                    f"de du truoc T6."
                ),
            )
        )
    return alerts


def pattern_alerts(
    summaries: list[EmployeeWeeklySummary],
    history_path: Path,
    *,
    as_of: date,
) -> list[PredictiveAlert]:
    """
    Phát hiện pattern hay quên log cùng weekday (từ lịch sử mock).
    history format: [{employee_id, work_date, missed_hours}]
    """
    if not history_path.is_file():
        return []

    rows = json.loads(history_path.read_text(encoding="utf-8"))
    by_emp: dict[str, Counter[int]] = defaultdict(Counter)
    for row in rows:
        if float(row.get("missed_hours", 0)) <= 0:
            continue
        d = date.fromisoformat(row["work_date"])
        by_emp[row["employee_id"]][d.weekday()] += 1

    today_wd = as_of.weekday()
    alerts: list[PredictiveAlert] = []
    for summary in summaries:
        counts = by_emp.get(summary.employee_id, Counter())
        if not counts:
            continue
        worst_wd, freq = counts.most_common(1)[0]
        if freq < 2 or worst_wd != today_wd:
            continue
        wd_names = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        alerts.append(
            PredictiveAlert(
                employee_id=summary.employee_id,
                display_name=summary.display_name,
                alert_type="pattern",
                message=(
                    f"Nhac: ban hay thieu log {wd_names[worst_wd]}. "
                    f"Hay log truoc khi ve nhe!"
                ),
            )
        )
    return alerts


def build_predictive_alerts(
    report: WeeklyReport,
    *,
    as_of: date,
    config: AuditConfig,
    data_dir: Path,
) -> list[PredictiveAlert]:
    alerts = midweek_pace_alerts(report, as_of=as_of, config=config)
    alerts.extend(
        pattern_alerts(
            report.summaries,
            data_dir / HISTORY_FILE,
            as_of=as_of,
        )
    )
    return alerts


def export_predictive_alerts(
    alerts: list[PredictiveAlert],
    output_dir: Path,
    *,
    week_label: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"predictive_{week_label}.json"
    path.write_text(
        json.dumps(
            [
                {
                    "employee_id": a.employee_id,
                    "display_name": a.display_name,
                    "alert_type": a.alert_type,
                    "message": a.message,
                }
                for a in alerts
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path
