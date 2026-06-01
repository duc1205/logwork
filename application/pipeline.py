"""Pipeline đối soát tuần — load → reconcile → export → notify."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from ..infra.data_loader import PeriodData, WeekData, load_month, load_week
from ..reporting.heatmap_export import export_heatmap_json
from ..domain.models import WeeklyReport
from ..infra.notify import build_notifications, export_notifications
from ..paths import MOCK_DIR, OUTPUT_DIR
from .predictive import build_predictive_alerts, export_predictive_alerts
from ..domain.reconciliation import ReconciliationEngine
from ..reporting.report_export import export_report_csv
from ..infra.teams_client import dispatch_notifications


def run_reconciliation(data: WeekData | PeriodData, *, monthly: bool = False) -> WeeklyReport:
    cfg = data.config
    engine = ReconciliationEngine(
        tolerance_hours=cfg.tolerance_hours,
        min_hours=cfg.min_hours,
        max_hours=cfg.max_hours,
        compensation_threshold=cfg.compensation_threshold,
        penalty_per_md=cfg.penalty_per_md,
        ot_rules=cfg.ot_rules,
    )
    if monthly and isinstance(data, PeriodData):
        return engine.reconcile_month(
            year=data.period_start.year,
            month=data.period_start.month,
            employees=data.employees,
            entries=data.entries,
            holidays=data.holidays,
            leaves=data.leaves,
            overtime=data.overtime,
        )
    if isinstance(data, WeekData):
        return engine.reconcile_week(
            anchor_date=data.anchor_date,
            employees=data.employees,
            entries=data.entries,
            holidays=data.holidays,
            leaves=data.leaves,
            overtime=data.overtime,
        )
    return engine.reconcile_period(
        period_start=data.period_start,
        period_end=data.period_end,
        employees=data.employees,
        entries=data.entries,
        holidays=data.holidays,
        leaves=data.leaves,
        overtime=data.overtime,
    )


def run_week(
    *,
    anchor_date: date | None = None,
    data_dir: Path | None = None,
    output_dir: Path | None = None,
    send_reminders: bool = False,
    export_heatmap: bool = False,
    run_predictive: bool = False,
    predictive_as_of: date | None = None,
    teams_webhook: str | None = None,
    use_live_jira: bool = False,
    use_plugin: bool = False,
) -> tuple[WeeklyReport, dict[str, Path]]:
    directory = data_dir or MOCK_DIR
    data = load_week(anchor_date, directory, use_live_jira=use_live_jira, use_plugin=use_plugin)
    report = run_reconciliation(data)
    paths: dict[str, Path] = {}

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        summary, compensation = export_report_csv(report, output_dir)
        paths["summary"] = summary
        paths["compensation"] = compensation

        if export_heatmap:
            paths["heatmap"] = export_heatmap_json(report, output_dir)

        if run_predictive:
            as_of = predictive_as_of or data.anchor_date
            alerts = build_predictive_alerts(
                report, as_of=as_of, config=data.config, data_dir=directory
            )
            paths["predictive"] = export_predictive_alerts(
                alerts, output_dir, week_label=report.week_start.isoformat()
            )

        if send_reminders:
            notifications = build_notifications(report)
            paths["reminders"] = export_notifications(
                notifications,
                output_dir,
                week_label=report.week_start.isoformat(),
            )
            result = dispatch_notifications(notifications, webhook_url=teams_webhook)
            if result.mode == "webhook":
                paths["teams_sent"] = output_dir / "teams_dispatch.log"
                paths["teams_sent"].write_text(
                    f"sent={result.sent} failed={result.failed}\n",
                    encoding="utf-8",
                )

    return report, paths


def run_month(
    *,
    year: int,
    month: int,
    data_dir: Path | None = None,
    output_dir: Path | None = None,
    use_live_jira: bool = False,
    use_plugin: bool = False,
    **kwargs,
) -> tuple[WeeklyReport, dict[str, Path]]:
    data = load_month(
        year, month, data_dir or MOCK_DIR,
        use_live_jira=use_live_jira,
        use_plugin=use_plugin,
    )
    report = run_reconciliation(data, monthly=True)
    paths: dict[str, Path] = {}

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        summary, compensation = export_report_csv(report, output_dir)
        paths["summary"] = summary
        paths["compensation"] = compensation

        if kwargs.get("export_heatmap"):
            paths["heatmap"] = export_heatmap_json(report, output_dir)
        if kwargs.get("run_predictive"):
            as_of = kwargs.get("predictive_as_of") or data.period_start
            alerts = build_predictive_alerts(
                report, as_of=as_of, config=data.config, data_dir=data_dir or MOCK_DIR
            )
            paths["predictive"] = export_predictive_alerts(
                alerts, output_dir, week_label=report.week_start.strftime("%Y-%m")
            )
        if kwargs.get("send_reminders"):
            notifications = build_notifications(report)
            paths["reminders"] = export_notifications(
                notifications,
                output_dir,
                week_label=report.week_start.strftime("%Y-%m"),
            )
            result = dispatch_notifications(
                notifications, webhook_url=kwargs.get("teams_webhook")
            )
            if result.mode == "webhook":
                paths["teams_sent"] = output_dir / "teams_dispatch.log"
                paths["teams_sent"].write_text(
                    f"sent={result.sent} failed={result.failed}\n",
                    encoding="utf-8",
                )

    return report, paths


def run_mock_week(
    *,
    anchor_date: date | None = None,
    output_dir: Path | None = None,
    **kwargs,
) -> WeeklyReport:
    report, _ = run_week(
        anchor_date=anchor_date,
        data_dir=MOCK_DIR,
        output_dir=output_dir or OUTPUT_DIR,
        **kwargs,
    )
    return report
