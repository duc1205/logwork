"""Tests cấu hình phạt và ngày nghỉ lễ."""

from __future__ import annotations

import json
import tempfile
from datetime import date
from pathlib import Path

from logwork.api.settings_store import (
    add_holiday,
    add_overtime_record,
    get_audit_settings,
    list_holidays,
    remove_holiday,
    remove_overtime_record,
    update_audit_settings,
    update_ot_rules,
)


def test_update_penalty_and_holidays_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "config.json").write_text(
            json.dumps(
                {
                    "min_hours": 8,
                    "max_hours": 8,
                    "tolerance_hours": 0.25,
                    "penalty_per_md": 20000,
                    "compensation_threshold": 2.0,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (root / "holidays.json").write_text(
            json.dumps(
                [{"holiday_date": "2026-05-01", "name": "1/5", "is_company_wide": True}],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        cfg = update_audit_settings(penalty_per_md=25000, data_dir=root)
        assert cfg["penalty_per_md"] == 25000

        raw = json.loads((root / "config.json").read_text(encoding="utf-8"))
        assert raw["penalty_per_md"] == 25000

        items = add_holiday(
            holiday_date=date(2026, 9, 2),
            name="Quốc khánh",
            data_dir=root,
        )
        assert len(items) == 2
        assert items[-1]["holiday_date"] == "2026-09-02"

        items = remove_holiday(date(2026, 5, 1), data_dir=root)
        assert len(items) == 1
        assert list_holidays(root)[0]["holiday_date"] == "2026-09-02"

        settings = get_audit_settings(root)
        assert settings["penalty_per_md"] == 25000


def test_ot_rules_and_overtime() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "config.json").write_text(
            json.dumps({"min_hours": 8, "ot_rules": {"max_ot_hours_per_day": 2, "max_daily_hours": 10}}),
            encoding="utf-8",
        )
        (root / "holidays.json").write_text("[]", encoding="utf-8")
        (root / "overtime.json").write_text("[]", encoding="utf-8")

        rules = update_ot_rules(max_ot_hours_per_day=3, accept_pending=True, data_dir=root)
        assert rules["max_ot_hours_per_day"] == 3
        assert rules["accept_pending"] is True

        items = add_overtime_record(
            employee_id="vuthif",
            ot_date=date(2026, 5, 20),
            ot_hours=2,
            reason="hotfix",
            data_dir=root,
        )
        assert len(items) == 1
        items = remove_overtime_record("vuthif", date(2026, 5, 20), data_dir=root)
        assert items == []


def run_tests() -> None:
    test_update_penalty_and_holidays_roundtrip()
    test_ot_rules_and_overtime()
    print("OK: settings store tests passed")


if __name__ == "__main__":
    run_tests()
