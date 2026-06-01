"""Sinh cột Note tự động cho báo cáo Excel."""

from __future__ import annotations

from datetime import date

from .compensation import CompensationPair
from .models import DailyAudit, Discrepancy, DiscrepancyType


def _fmt_day(d: date) -> str:
    return d.strftime("%d/%m")


def generate_employee_note(
    daily_audits: list[DailyAudit],
    discrepancies: list[Discrepancy],
    compensation_pairs: list[CompensationPair],
) -> str:
    """Gộp các vi phạm thành chuỗi Note như format QA."""
    parts: list[str] = []

    missing_days = sorted(
        d.work_date
        for d in discrepancies
        if d.discrepancy_type == DiscrepancyType.MISSING_DAY
    )
    if missing_days:
        days_str = ", ".join(_fmt_day(d) for d in missing_days)
        parts.append(f"Không log ngày {days_str}")

    under = [
        d for d in discrepancies if d.discrepancy_type == DiscrepancyType.UNDER_HOURS
    ]
    for d in under:
        parts.append(f"Log thiếu {d.delta_hours:.0f}h ngày {_fmt_day(d.work_date)}")

    for pair in compensation_pairs:
        parts.append(
            f"Bù trừ: {_fmt_day(pair.under_day)} thiếu {pair.under_hours:.0f}h "
            f"↔ {_fmt_day(pair.over_day)} thừa {pair.over_hours:.0f}h"
        )

    over = [d for d in discrepancies if d.discrepancy_type == DiscrepancyType.OVER_HOURS]
    for d in over:
        if not any(
            p.over_day == d.work_date
            for p in compensation_pairs
            if p.employee_id == d.employee_id
        ):
            parts.append(f"Log thừa {d.delta_hours:.0f}h ngày {_fmt_day(d.work_date)}")

    return "; ".join(parts) if parts else ""
