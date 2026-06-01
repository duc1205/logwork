"""Parse tham số kỳ từ query string API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..domain.period_utils import month_range, parse_month, week_range


@dataclass(frozen=True)
class ResolvedPeriod:
    start: date
    end: date
    mode: str  # week | month
    anchor: date | None = None


def resolve_period(
    *,
    week: date | None = None,
    month: str | None = None,
    start: date | None = None,
    end: date | None = None,
) -> ResolvedPeriod:
    if month:
        year, mon = parse_month(month)
        ps, pe = month_range(year, mon)
        return ResolvedPeriod(start=ps, end=pe, mode="month")
    if start and end:
        return ResolvedPeriod(start=start, end=end, mode="week", anchor=start)
    anchor = week or date.today()
    ps, pe = week_range(anchor)
    return ResolvedPeriod(start=ps, end=pe, mode="week", anchor=anchor)
