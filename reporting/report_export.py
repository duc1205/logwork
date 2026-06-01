"""Xuất báo cáo CSV — format golden file QA (cột tính theo MD)."""

from __future__ import annotations

import csv
import io
from pathlib import Path

from ..domain.models import WeeklyReport
from ..domain.penalty import hours_to_md

SUMMARY_HEADER = [
    "Account",
    "Full Name",
    "Holiday",
    "Actual (MD)",
    "Required (MD)",
    "Missed (MD)",
    "Penalty (VND)",
    "Target (MD)",
    "Note",
]

COMP_HEADER = [
    "Account",
    "Under Day",
    "Over Day",
    "Under Hours",
    "Over Hours",
    "Confidence",
    "Message",
]


def _report_label(report: WeeklyReport) -> str:
    if (
        report.week_start.day == 1
        and report.week_end.month == report.week_start.month
        and report.week_end.day >= 28
    ):
        return report.week_start.strftime("%Y-%m")
    return report.week_start.isoformat()


def report_summary_csv_text(report: WeeklyReport) -> str:
    """CSV summary in-memory — cùng format golden QA."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(SUMMARY_HEADER)
    for s in report.summaries:
        writer.writerow(
            [
                s.employee_id,
                s.display_name,
                s.holiday_count,
                f"{hours_to_md(s.actual_hours):.2f}",
                f"{hours_to_md(s.required_hours):.2f}",
                f"{hours_to_md(s.missed_hours):.2f}",
                s.penalty,
                f"{s.target_md:.1f}",
                s.note,
            ]
        )
    return buf.getvalue()


def report_compensation_csv_text(report: WeeklyReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(COMP_HEADER)
    for s in report.summaries:
        for p in s.compensation_pairs:
            conf = p.confidence.value if hasattr(p.confidence, "value") else str(p.confidence)
            writer.writerow(
                [
                    p.employee_id,
                    p.under_day.isoformat(),
                    p.over_day.isoformat(),
                    f"{p.under_hours:.1f}",
                    f"{p.over_hours:.1f}",
                    conf,
                    p.message,
                ]
            )
    return buf.getvalue()


def export_report_csv(report: WeeklyReport, output_dir: Path) -> tuple[Path, Path]:
    label = _report_label(report)
    summary_path = output_dir / f"logwork_{label}_summary.csv"
    comp_path = output_dir / f"logwork_{label}_compensation.csv"
    summary_path.write_text(report_summary_csv_text(report), encoding="utf-8-sig")
    comp_path.write_text(report_compensation_csv_text(report), encoding="utf-8-sig")
    return summary_path, comp_path
