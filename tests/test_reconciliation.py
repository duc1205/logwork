"""Unit test engine đối soát — chạy: python -m logwork test"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from ..domain.models import Employee, EmployeeLeave, Holiday, LeaveType, OvertimeRecord, OvertimeStatus, TimesheetEntry
from ..domain.penalty import calculate_penalty, hours_to_md
from ..domain.reconciliation import ReconciliationEngine


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _parse_entry(raw: dict) -> TimesheetEntry:
    return TimesheetEntry(
        employee_id=raw["employee_id"],
        work_date=date.fromisoformat(raw["work_date"]),
        hours=raw["hours"],
    )


def test_penalty_formula() -> None:
    assert hours_to_md(4) == 0.5
    assert calculate_penalty(4) == 10_000
    assert calculate_penalty(8) == 20_000
    assert calculate_penalty(0) == 0


def test_layer1_basic() -> None:
    engine = ReconciliationEngine()
    emp = Employee("u1", "Test User", "t@x.com")
    holidays = [Holiday(date(2026, 5, 1), "Lễ")]
    entries = [
        TimesheetEntry("u1", date(2026, 5, 18), 0),
        TimesheetEntry("u1", date(2026, 5, 19), 5),
        TimesheetEntry("u1", date(2026, 5, 20), 8),
    ]
    report = engine.reconcile_week(
        anchor_date=date(2026, 5, 20),
        employees=[emp],
        entries=entries,
        holidays=holidays,
    )
    types = {
        d.discrepancy_type.value
        for d in report.discrepancies
        if d.employee_id == "u1"
    }
    assert "missing_day" in types or "under_hours" in types
    summary = report.summaries[0]
    assert summary.penalty > 0


def test_leave_exempt() -> None:
    engine = ReconciliationEngine()
    emp = Employee("u2", "Leave User", "l@x.com")
    day = date(2026, 5, 19)
    report = engine.reconcile_week(
        anchor_date=day,
        employees=[emp],
        entries=[],
        holidays=[],
        leaves=[
            EmployeeLeave("u2", day, LeaveType.ANNUAL, source="excel"),
        ],
    )
    audit = next(a for a in report.summaries[0].daily_audits if a.work_date == day)
    assert audit.required_hours == 0
    assert audit.missed_hours == 0


def test_ot_raises_valid_max() -> None:
    engine = ReconciliationEngine()
    emp = Employee("u3", "OT User", "o@x.com")
    day = date(2026, 5, 19)
    report = engine.reconcile_week(
        anchor_date=day,
        employees=[emp],
        entries=[TimesheetEntry("u3", day, 10.0)],
        holidays=[],
        overtime=[
            OvertimeRecord("u3", day, 2.0, status=OvertimeStatus.APPROVED),
        ],
    )
    over_types = [
        d.discrepancy_type.value
        for d in report.discrepancies
        if d.discrepancy_type.value == "over_hours"
    ]
    assert over_types == []


def test_ot_cap_max_daily() -> None:
    from ..domain.models import OtRules

    engine = ReconciliationEngine(
        ot_rules=OtRules(max_ot_hours_per_day=4, max_daily_hours=10, ot_grace_hours=0),
    )
    emp = Employee("u4", "Cap User", "c@x.com")
    day = date(2026, 5, 19)
    report = engine.reconcile_week(
        anchor_date=day,
        employees=[emp],
        entries=[TimesheetEntry("u4", day, 11.0)],
        holidays=[],
        overtime=[OvertimeRecord("u4", day, 4.0, status=OvertimeStatus.APPROVED)],
    )
    overs = [d for d in report.discrepancies if d.discrepancy_type.value == "over_hours"]
    assert len(overs) == 1
    assert abs(overs[0].delta_hours - 1.0) < 0.01


def test_golden_week_compensation() -> None:
    path = FIXTURES_DIR / "golden_week.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    emp_raw = data["employee"]
    emp = Employee(
        emp_raw["account_id"],
        emp_raw["display_name"],
        emp_raw["email"],
    )
    entries = [_parse_entry(e) for e in data["entries"]]
    engine = ReconciliationEngine()
    report = engine.reconcile_week(
        anchor_date=date.fromisoformat(data["anchor_date"]),
        employees=[emp],
        entries=entries,
        holidays=[],
    )

    exp = data["expected"]
    summary = report.summaries[0]
    assert summary.actual_hours == exp["total_actual"]
    assert summary.required_hours == exp["total_required"]
    assert len(summary.compensation_pairs) == exp["compensation_pairs"]

    layer1 = [
        d
        for d in report.discrepancies
        if d.discrepancy_type.value
        in ("missing_day", "under_hours", "over_hours")
    ]
    assert len(layer1) >= exp["layer1_violations"]
    assert summary.penalty >= exp["penalty_min"]

    for fragment in exp["note_contains"]:
        assert fragment in summary.note


def test_mock_pipeline() -> None:
    from ..application.pipeline import run_mock_week

    report = run_mock_week()
    assert report.employees_checked == 6
    assert report.total_penalty > 0

    by_account = {s.employee_id: s for s in report.summaries}
    assert by_account["nguyenvana"].penalty == 0
    assert by_account["levanc"].penalty == 20_000
    assert len(by_account["levanc"].compensation_pairs) == 1
    assert by_account["phamthid"].missed_hours == 0
    assert "tranthib" in by_account and by_account["tranthib"].missed_hours > 0


def test_csv_import_matches_mock() -> None:
    from ..infra.excel_import import import_timesheet_csv
    from ..paths import MOCK_DIR
    from ..application.pipeline import run_week

    csv_entries = import_timesheet_csv(MOCK_DIR / "jira_timesheet.csv")
    assert len(csv_entries) >= 20

    report, _ = run_week(data_dir=MOCK_DIR, output_dir=None)
    assert report.employees_checked == 6
    assert report.total_penalty > 0


def test_notifications() -> None:
    from ..infra.notify import build_notifications
    from ..application.pipeline import run_week

    report, _ = run_week(output_dir=None)
    notes = build_notifications(report)
    assert len(notes) >= 3
    assert any("tranthib" in n.employee_id or "Tran" in n.display_name for n in notes)


def test_dedup_leaves() -> None:
    from ..infra.dedup import dedup_leaves
    from ..domain.models import EmployeeLeave, LeaveType
    from datetime import date

    d = date(2026, 5, 21)
    a = EmployeeLeave("phamthid", d, LeaveType.ANNUAL, source="excel")
    b = EmployeeLeave("phamthid", d, LeaveType.ANNUAL, source="jira")
    merged, dups = dedup_leaves([a, b])
    assert len(merged) == 1
    assert merged[0].source == "jira"
    assert len(dups) == 1


def test_predictive_and_heatmap() -> None:
    import tempfile
    from datetime import date
    from pathlib import Path

    from ..paths import MOCK_DIR
    from ..application.pipeline import run_week

    with tempfile.TemporaryDirectory() as td:
        report, paths = run_week(
            data_dir=MOCK_DIR,
            output_dir=Path(td),
            run_predictive=True,
            predictive_as_of=date(2026, 5, 20),
            export_heatmap=True,
        )
        assert report.employees_checked == 6
        assert paths["heatmap"].is_file()
        assert paths["predictive"].is_file()


def test_golden_validate_sample() -> None:
    from ..reporting.golden_validate import validate_golden_file
    from ..paths import FIXTURES_DIR

    count, errors, warnings = validate_golden_file(FIXTURES_DIR / "golden" / "report_sample.csv")
    assert count == 3
    assert errors == []


def test_month_reconcile() -> None:
    from ..application.pipeline import run_month

    report, _ = run_month(year=2026, month=5, output_dir=None)
    assert report.week_start == date(2026, 5, 1)
    assert report.week_end == date(2026, 5, 31)
    assert report.employees_checked == 6
    for s in report.summaries:
        assert s.target_md > 0


def test_jira_client_fallback() -> None:
    from ..infra.jira_client import (
        LiveJiraClient,
        JiraConfig,
        author_to_employee_id,
        infer_jira_api_version,
        _parse_jira_started,
    )
    from ..paths import MOCK_DIR

    client = LiveJiraClient(JiraConfig(), fallback_dir=MOCK_DIR)
    entries = client.fetch_worklogs(
        start_date=date(2026, 5, 18),
        end_date=date(2026, 5, 22),
    )
    assert len(entries) > 0
    assert not client.api_enabled

    assert author_to_employee_id({"emailAddress": "nguyenvana@company.vn"}, field="email") == "nguyenvana"
    assert author_to_employee_id({"name": "nguyenvana"}, field="name") == "nguyenvana"
    assert infer_jira_api_version("https://jira.tinhvan.com") == 2
    assert infer_jira_api_version("https://foo.atlassian.net") == 3
    assert _parse_jira_started("2026-05-18T09:00:00.000+0700") == date(2026, 5, 18)


def test_monthly_scheduler() -> None:
    from ..application.scheduler import JobType, run_job
    from ..paths import OUTPUT_DIR

    log = run_job(JobType.MONTHLY_CLOSE, month="2026-05", output_dir=OUTPUT_DIR)
    assert log.is_file()
    text = log.read_text(encoding="utf-8")
    assert "job=monthly_close" in text
    assert "period=2026-05" in text


def run_tests() -> None:
    test_penalty_formula()
    test_layer1_basic()
    test_leave_exempt()
    test_ot_raises_valid_max()
    test_ot_cap_max_daily()
    test_golden_week_compensation()
    test_mock_pipeline()
    test_csv_import_matches_mock()
    test_notifications()
    test_dedup_leaves()
    test_predictive_and_heatmap()
    test_golden_validate_sample()
    test_month_reconcile()
    test_jira_client_fallback()
    test_monthly_scheduler()

    from .test_period_query import (
        test_clip_report,
        test_effective_as_of_clips_future_month,
        test_golden_compare_maps,
        test_heatmap_from_mock_report,
        test_live_notification_batch,
        test_predictive_mock_week,
        test_report_summary_csv,
        test_resolve_month,
        test_resolve_week_by_anchor,
        test_resolve_week_by_start_end,
    )

    test_resolve_week_by_start_end()
    test_resolve_week_by_anchor()
    test_resolve_month()
    test_effective_as_of_clips_future_month()
    test_heatmap_from_mock_report()
    test_golden_compare_maps()
    test_predictive_mock_week()
    test_clip_report()
    test_report_summary_csv()
    test_live_notification_batch()

    from .test_reminder_dispatch import run_tests as run_reminder_tests

    run_reminder_tests()

    from .test_wednesday_scheduler import run_tests as run_wednesday_scheduler_tests

    run_wednesday_scheduler_tests()

    from .test_settings_store import run_tests as run_settings_tests

    run_settings_tests()

    from .test_auth_roles import run_tests as run_auth_role_tests

    run_auth_role_tests()

    print("OK: all reconciliation tests passed")


if __name__ == "__main__":
    run_tests()
