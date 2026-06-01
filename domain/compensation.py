"""Lớp 2 — Phát hiện bù trừ bất thường giữa các ngày trong tuần."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from .models import DailyAudit


class CompensationConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class CompensationPair:
    employee_id: str
    under_day: date
    over_day: date
    under_hours: float  # số giờ thiếu ở ngày under_day
    over_hours: float   # số giờ thừa ở ngày over_day
    confidence: CompensationConfidence
    message: str


def _confidence(delta_diff: float, threshold: float) -> CompensationConfidence:
    ratio = delta_diff / threshold if threshold > 0 else delta_diff
    if ratio <= 0.25:
        return CompensationConfidence.HIGH
    if ratio <= 0.5:
        return CompensationConfidence.MEDIUM
    return CompensationConfidence.LOW


def detect_compensation(
    employee_id: str,
    daily_audits: list[DailyAudit],
    *,
    min_hours: float = 8.0,
    max_hours: float = 8.0,
    tolerance_hours: float = 0.25,
    compensation_threshold: float = 2.0,
) -> list[CompensationPair]:
    """
    Phát hiện pattern bù trừ: ngày A thiếu Xh + ngày B thừa Yh với X ≈ Y.

    Chỉ chạy khi tổng tuần đủ (sum actual >= sum required) nhưng có ngày vi phạm.
    """
    if not daily_audits:
        return []

    total_required = sum(d.required_hours for d in daily_audits)
    total_actual = sum(d.actual_hours for d in daily_audits)
    if total_actual < total_required - tolerance_hours:
        return []

    under_days: list[tuple[date, float]] = []
    over_days: list[tuple[date, float]] = []

    for d in daily_audits:
        if d.required_hours <= 0:
            continue
        if d.actual_hours < min_hours - tolerance_hours:
            under_days.append((d.work_date, min_hours - d.actual_hours))
        elif d.actual_hours > max_hours + tolerance_hours:
            over_days.append((d.work_date, d.actual_hours - max_hours))

    if not under_days or not over_days:
        return []

    pairs: list[CompensationPair] = []
    used_over: set[date] = set()

    for under_day, under_delta in under_days:
        best_match: CompensationPair | None = None
        best_diff = float("inf")

        for over_day, over_delta in over_days:
            if over_day in used_over:
                continue
            delta_diff = abs(under_delta - over_delta)
            if delta_diff <= compensation_threshold and delta_diff < best_diff:
                conf = _confidence(delta_diff, compensation_threshold)
                best_match = CompensationPair(
                    employee_id=employee_id,
                    under_day=under_day,
                    over_day=over_day,
                    under_hours=under_delta,
                    over_hours=over_delta,
                    confidence=conf,
                    message=(
                        f"Bù trừ: {under_day.isoformat()} thiếu {under_delta:.1f}h "
                        f"↔ {over_day.isoformat()} thừa {over_delta:.1f}h "
                        f"({conf.value})"
                    ),
                )
                best_diff = delta_diff

        if best_match:
            pairs.append(best_match)
            used_over.add(best_match.over_day)

    return pairs
