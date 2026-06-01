"""Tiện ích khoảng thời gian cho API (clip ngày tương lai)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from ..domain.period_utils import week_range
from ..reporting.heatmap_export import build_heatmap_payload
from .schemas import CompensationItem, DailyAuditItem, HeatmapCell, HeatmapResponse, WeeklySummaryResponse


def effective_as_of_range(period_start: date, period_end: date) -> date:
    """Tuần/tháng quá khứ → tính hết kỳ; kỳ hiện tại → chỉ đến hôm nay."""
    return min(date.today(), period_end)


def effective_as_of(anchor: date) -> date:
    """Backward compat: tuần chứa anchor."""
    week_start, week_end = week_range(anchor)
    return effective_as_of_range(week_start, week_end)


def _compensation_items(pairs, as_of: date) -> list[CompensationItem]:
    items: list[CompensationItem] = []
    for p in pairs:
        if p.under_day > as_of or p.over_day > as_of:
            continue
        conf = p.confidence.value if hasattr(p.confidence, "value") else str(p.confidence)
        items.append(
            CompensationItem(
                under_day=p.under_day,
                over_day=p.over_day,
                under_hours=p.under_hours,
                over_hours=p.over_hours,
                confidence=conf,
                message=p.message,
            )
        )
    return items


def clip_summary(summary: WeeklySummaryResponse, as_of: date) -> WeeklySummaryResponse:
    """Bỏ ngày tương lai và cập nhật lại tổng."""
    audits = [a for a in summary.daily_audits if a.work_date <= as_of]
    comp = [c for c in summary.compensation_pairs if c.under_day <= as_of and c.over_day <= as_of]
    return summary.model_copy(
        update={
            "as_of": as_of,
            "daily_audits": audits,
            "compensation_pairs": comp,
            "actual_hours": sum(a.actual_hours for a in audits),
            "required_hours": sum(a.required_hours for a in audits),
            "missed_hours": sum(a.missed_hours for a in audits),
            "penalty": sum(a.penalty for a in audits),
            "holiday_count": sum(1 for a in audits if a.is_holiday),
        }
    )


def summary_from_report(
    report,
    account_id: str,
    as_of: date,
    *,
    data_source: str = "plugin",
) -> WeeklySummaryResponse | None:
    for s in report.summaries:
        if s.employee_id.lower() == account_id.lower():
            return clip_summary(
                WeeklySummaryResponse(
                    week_start=report.week_start,
                    week_end=report.week_end,
                    as_of=as_of,
                    data_source=data_source,
                    display_name=s.display_name,
                    account_id=s.employee_id,
                    holiday_count=s.holiday_count,
                    actual_hours=s.actual_hours,
                    required_hours=s.required_hours,
                    missed_hours=s.missed_hours,
                    penalty=s.penalty,
                    target_md=s.target_md,
                    note=s.note,
                    daily_audits=[
                        DailyAuditItem(
                            work_date=a.work_date,
                            required_hours=a.required_hours,
                            actual_hours=a.actual_hours,
                            missed_hours=a.missed_hours,
                            penalty=a.penalty,
                            is_holiday=a.is_holiday,
                            is_leave=a.is_leave,
                        )
                        for a in s.daily_audits
                    ],
                    compensation_pairs=_compensation_items(s.compensation_pairs, as_of),
                ),
                as_of,
            )
    return None


def clip_report(report, as_of: date):
    """Clip mọi summary trong report đến as_of — khớp số liệu dashboard/export."""
    summaries = []
    for s in report.summaries:
        audits = [a for a in s.daily_audits if a.work_date <= as_of]
        comp = [p for p in s.compensation_pairs if p.under_day <= as_of and p.over_day <= as_of]
        summaries.append(
            replace(
                s,
                daily_audits=audits,
                compensation_pairs=comp,
                actual_hours=sum(a.actual_hours for a in audits),
                required_hours=sum(a.required_hours for a in audits),
                missed_hours=sum(a.missed_hours for a in audits),
                penalty=sum(a.penalty for a in audits),
                holiday_count=sum(1 for a in audits if a.is_holiday),
            )
        )
    total_penalty = sum(s.penalty for s in summaries)
    return replace(report, summaries=summaries, total_penalty=total_penalty)


def heatmap_from_report(
    report,
    as_of: date,
    *,
    data_source: str = "plugin",
    period_mode: str = "week",
    account_id: str | None = None,
    admin: bool = False,
) -> HeatmapResponse:
    payload = build_heatmap_payload(report)
    cells: list[HeatmapCell] = []
    for raw in payload["cells"]:
        cell_date = date.fromisoformat(raw["date"])
        if cell_date > as_of:
            continue
        if not admin and account_id and raw["employee_id"].lower() != account_id.lower():
            continue
        cells.append(
            HeatmapCell(
                employee_id=raw["employee_id"],
                display_name=raw["display_name"],
                date=cell_date,
                actual=raw["actual"],
                required=raw["required"],
                status=raw["status"],
                color=raw["color"],
                penalty=raw["penalty"],
                is_leave=raw["is_leave"],
                is_holiday=raw["is_holiday"],
            )
        )
    return HeatmapResponse(
        week_start=date.fromisoformat(payload["week_start"]),
        week_end=date.fromisoformat(payload["week_end"]),
        as_of=as_of,
        period_mode=period_mode,
        data_source=data_source,
        cells=cells,
    )
