"""
CLI logwork. Chạy từ thư mục gốc repo:

  python -m logwork test
  python -m logwork reconcile --remind --heatmap --predict
  python -m logwork schedule --job predictive
  TEAMS_WEBHOOK_URL=https://... python -m logwork reconcile --remind --teams
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="logwork",
        description="Tu dong hoa doi soat logwork Jira (De bai so 5)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("test", help="Chay unit test")

    reconcile_p = sub.add_parser("reconcile", help="Doi soat tuan (mock/CSV)")
    reconcile_p.add_argument("--date", type=str, default=None, help="YYYY-MM-DD (tuan)")
    reconcile_p.add_argument(
        "--month", type=str, default=None, help="YYYY-MM (doi soat ca thang, giong golden QA)"
    )
    reconcile_p.add_argument("--data-dir", type=str, default=None)
    reconcile_p.add_argument("--output", type=str, default="logwork/output")
    reconcile_p.add_argument("--remind", action="store_true", help="Sinh file nhac")
    reconcile_p.add_argument("--teams", action="store_true", help="Gui Teams webhook (env TEAMS_WEBHOOK_URL)")
    reconcile_p.add_argument("--heatmap", action="store_true", help="Xuat heatmap JSON")
    reconcile_p.add_argument("--predict", action="store_true", help="Canh bao som pace tuan")
    reconcile_p.add_argument("--live-jira", action="store_true", help="Lay worklog tu Jira API (env JIRA_*)")
    reconcile_p.add_argument("--plugin", action="store_true", help="Lay worklog tu plugin ProjectTimesheet (env JIRA_*)")
    reconcile_p.add_argument(
        "--predict-as-of", type=str, default=None, help="Ngay gia dinh chay predictive (YYYY-MM-DD)"
    )

    preview_p = sub.add_parser("preview", help="Xem truoc import CSV")
    preview_p.add_argument("--file", type=str, required=True)

    schedule_p = sub.add_parser("schedule", help="Dry-run job theo lich")
    schedule_p.add_argument(
        "--job",
        type=str,
        choices=["predictive", "reminder", "weekly_close", "monthly_close"],
        default="weekly_close",
    )
    schedule_p.add_argument("--date", type=str, default=None)
    schedule_p.add_argument("--month", type=str, default=None, help="YYYY-MM (cho monthly_close)")
    schedule_p.add_argument("--live-jira", action="store_true")
    schedule_p.add_argument("--output", type=str, default="logwork/output")

    golden_p = sub.add_parser("validate-golden", help="Kiem tra golden file QA (quy tac penalty)")
    golden_p.add_argument(
        "--file",
        type=str,
        default="logwork/fixtures/golden/report_sample.csv",
        help="Duong dan CSV golden",
    )

    compare_p = sub.add_parser(
        "compare-golden",
        help="So sanh summary engine vs golden file (theo Account)",
    )
    compare_p.add_argument("--engine", type=str, required=True, help="summary.csv tu engine")
    compare_p.add_argument(
        "--golden",
        type=str,
        default="logwork/fixtures/golden/report_sample.csv",
        help="CSV golden QA",
    )

    args = parser.parse_args(argv)

    if args.command == "test":
        from .tests.test_reconciliation import run_tests

        run_tests()
    elif args.command == "reconcile":
        from .paths import MOCK_DIR
        from .domain.period_utils import parse_month
        from .application.pipeline import run_month, run_week
        from .infra.teams_client import get_webhook_url

        data_dir = Path(args.data_dir) if args.data_dir else MOCK_DIR
        predict_as_of = (
            date.fromisoformat(args.predict_as_of) if args.predict_as_of else None
        )
        teams = args.teams or bool(get_webhook_url())
        kw = dict(
            output_dir=Path(args.output),
            send_reminders=args.remind or teams,
            export_heatmap=args.heatmap,
            run_predictive=args.predict,
            predictive_as_of=predict_as_of,
            teams_webhook=get_webhook_url() if teams else None,
            use_live_jira=args.live_jira,
            use_plugin=args.plugin,
        )

        if args.month:
            year, month = parse_month(args.month)
            report, paths = run_month(
                year=year, month=month, data_dir=data_dir, **kw
            )
        else:
            anchor = date.fromisoformat(args.date) if args.date else None
            report, paths = run_week(
                anchor_date=anchor,
                data_dir=data_dir,
                **kw,
            )
        label = (
            f"Month {report.week_start.strftime('%Y-%m')}"
            if args.month
            else f"Week {report.week_start} -> {report.week_end}"
        )
        print(
            f"{label}: "
            f"{report.employees_checked} employees, "
            f"{len(report.discrepancies)} items, "
            f"penalty {report.total_penalty:,} VND"
        )
        for name, p in paths.items():
            print(f"  {name}: {p}")
    elif args.command == "preview":
        from .infra.excel_import import preview_csv

        info = preview_csv(Path(args.file))
        print(f"file: {info['file']} ({info['kind']})")
        print(f"headers: {info['headers']}")
        for i, row in enumerate(info["sample_rows"], 1):
            print(f"  row{i}: {row}")
    elif args.command == "schedule":
        from .application.scheduler import JobType, run_job

        anchor = date.fromisoformat(args.date) if args.date else None
        log = run_job(
            JobType(args.job),
            anchor_date=anchor,
            month=args.month,
            output_dir=Path(args.output),
            use_live_jira=args.live_jira,
        )
        print(f"Scheduler log: {log}")
    elif args.command == "validate-golden":
        from .reporting.golden_validate import validate_golden_file

        path = Path(args.file)
        count, errors, warnings = validate_golden_file(path)
        print(f"Golden file: {path.name} — {count} rows")
        for w in warnings:
            print(f"  WARN: {w}")
        if errors:
            print(f"FAILED: {len(errors)} error(s)")
            for e in errors:
                print(f"  - {e}")
            return 1
        print("OK: penalty = missed_md x 20,000")
    elif args.command == "compare-golden":
        from .reporting.golden_validate import compare_engine_to_golden

        errors, warnings = compare_engine_to_golden(
            Path(args.engine), Path(args.golden)
        )
        for w in warnings:
            print(f"  WARN: {w}")
        if errors:
            print(f"FAILED: {len(errors)} mismatch(es)")
            for e in errors:
                print(f"  - {e}")
            return 1
        print("OK: engine summary matches golden (within tolerance)")
    else:
        parser.error(f"Lenh khong ho tro: {args.command}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
