"""Predictive alerts cho API — chỉ pace tuần (không dùng mock history)."""

from __future__ import annotations

from datetime import date

from ..application.predictive import PredictiveAlert, midweek_pace_alerts
from .live_config import load_audit_config
from .schemas import PredictiveAlertItem


def predictive_items(
    report,
    as_of: date,
    *,
    account_id: str | None = None,
    admin: bool = False,
) -> list[PredictiveAlertItem]:
    if (report.week_end - report.week_start).days + 1 > 7:
        return []

    config = load_audit_config()
    alerts: list[PredictiveAlert] = midweek_pace_alerts(
        report, as_of=as_of, config=config,
    )

    if not admin and account_id:
        alerts = [a for a in alerts if a.employee_id.lower() == account_id.lower()]

    return [
        PredictiveAlertItem(
            employee_id=a.employee_id,
            display_name=a.display_name,
            alert_type=a.alert_type,
            message=a.message,
        )
        for a in alerts
    ]
