"""Tính phạt logwork theo công thức nghiệp vụ QA."""

from __future__ import annotations

# 20.000 VNĐ / MD (8 giờ)
DEFAULT_PENALTY_PER_MD = 20_000
HOURS_PER_MD = 8.0


def hours_to_md(hours: float) -> float:
    """Quy đổi giờ thiếu sang man-day."""
    if hours <= 0:
        return 0.0
    return hours / HOURS_PER_MD


def calculate_penalty(
    missed_hours: float,
    *,
    penalty_per_md: float = DEFAULT_PENALTY_PER_MD,
) -> int:
    """
    Penalty = Missed MD × penalty_per_md
    Ví dụ: thiếu 4h → 0.5 MD → 10.000 VNĐ
    """
    if missed_hours <= 0:
        return 0
    return int(round(hours_to_md(missed_hours) * penalty_per_md))
