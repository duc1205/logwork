"""Tiện ích khoảng thời gian — tuần ISO, tháng calendar."""

from __future__ import annotations

import calendar
from datetime import date, timedelta


def week_range(anchor: date) -> tuple[date, date]:
    """Tuần ISO: Thứ 2 → Chủ nhật."""
    start = anchor - timedelta(days=anchor.weekday())
    return start, start + timedelta(days=6)


def month_range(year: int, month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def parse_month(value: str) -> tuple[int, int]:
    """'2026-05' → (2026, 5)."""
    year_s, month_s = value.strip().split("-", 1)
    return int(year_s), int(month_s)
