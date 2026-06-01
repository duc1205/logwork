"""Tests for API period query resolution."""

from __future__ import annotations

from datetime import date

from logwork.api.period_helpers import effective_as_of_range
from logwork.api.period_query import resolve_period


def test_resolve_week_by_start_end() -> None:
    period = resolve_period(start=date(2026, 5, 26), end=date(2026, 6, 1))
    assert period.mode == "week"
    assert period.start == date(2026, 5, 26)
    assert period.end == date(2026, 6, 1)
    assert period.anchor == date(2026, 5, 26)


def test_resolve_week_by_anchor() -> None:
    period = resolve_period(week=date(2026, 5, 28))
    assert period.mode == "week"
    assert period.start == date(2026, 5, 25)
    assert period.end == date(2026, 5, 31)


def test_resolve_month() -> None:
    period = resolve_period(month="2026-05")
    assert period.mode == "month"
    assert period.start == date(2026, 5, 1)
    assert period.end == date(2026, 5, 31)
    assert period.anchor is None


def test_effective_as_of_clips_future_month() -> None:
    as_of = effective_as_of_range(date(2026, 6, 1), date(2026, 6, 30))
    assert as_of <= date.today()


def test_heatmap_from_mock_report() -> None:
    from logwork.api.period_helpers import heatmap_from_report
    from logwork.application.pipeline import run_mock_week

    report = run_mock_week()
    hm = heatmap_from_report(report, date(2026, 5, 24), data_source="mock", admin=True)
    assert len(hm.cells) > 0
    assert hm.week_start == report.week_start


def test_golden_compare_maps() -> None:
    from logwork.application.pipeline import run_mock_week
    from logwork.reporting.golden_validate import (
        compare_golden_maps,
        report_to_golden_map,
    )

    report = run_mock_week()
    engine = report_to_golden_map(report)
    errors, warnings = compare_golden_maps(engine, engine)
    assert errors == []
    assert warnings == []


def test_predictive_mock_week() -> None:
    from logwork.api.predictive_helpers import predictive_items
    from logwork.application.pipeline import run_mock_week

    report = run_mock_week()
    # Thứ Ba tuần mock (2026-05-20)
    items = predictive_items(report, date(2026, 5, 20), admin=True)
    assert isinstance(items, list)


def test_clip_report() -> None:
    from logwork.api.period_helpers import clip_report
    from logwork.application.pipeline import run_mock_week

    report = run_mock_week()
    as_of = report.week_start
    clipped = clip_report(report, as_of)
    assert len(clipped.summaries) == len(report.summaries)
    for s in clipped.summaries:
        assert all(a.work_date <= as_of for a in s.daily_audits)


def test_report_summary_csv() -> None:
    from logwork.application.pipeline import run_mock_week
    from logwork.reporting.report_export import report_summary_csv_text

    report = run_mock_week()
    text = report_summary_csv_text(report)
    lines = text.strip().splitlines()
    assert "Account" in lines[0] and "Penalty (VND)" in lines[0]
    assert len(lines) >= 2


def test_live_notification_batch() -> None:
    from logwork.api.notification_store import is_live_notification_batch

    assert is_live_notification_batch({"data_source": "plugin_team"}) is True
    assert is_live_notification_batch({"data_source": "mock"}) is False
    assert is_live_notification_batch({}) is False
