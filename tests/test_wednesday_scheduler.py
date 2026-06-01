"""Tests lịch job nhắc 17:00 thứ Tư."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from logwork.api.scheduler_service import get_schedule_info
from logwork.api.wednesday_job import next_wednesday_17h

TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def test_next_wednesday_from_monday() -> None:
    mon = datetime(2026, 6, 1, 10, 0, tzinfo=TZ)
    nxt = next_wednesday_17h(mon)
    assert nxt == datetime(2026, 6, 3, 17, 0, tzinfo=TZ)


def test_next_wednesday_same_day_before_17() -> None:
    wed_am = datetime(2026, 6, 3, 9, 30, tzinfo=TZ)
    assert next_wednesday_17h(wed_am) == datetime(2026, 6, 3, 17, 0, tzinfo=TZ)


def test_next_wednesday_same_day_after_17() -> None:
    wed_pm = datetime(2026, 6, 3, 18, 0, tzinfo=TZ)
    assert next_wednesday_17h(wed_pm) == datetime(2026, 6, 10, 17, 0, tzinfo=TZ)


def test_next_wednesday_from_thursday() -> None:
    thu = datetime(2026, 6, 4, 8, 0, tzinfo=TZ)
    assert next_wednesday_17h(thu) == datetime(2026, 6, 10, 17, 0, tzinfo=TZ)


def test_schedule_info_has_wednesday_fields() -> None:
    info = get_schedule_info()
    assert info["day_of_week"] == "wednesday"
    assert info["day_of_week_vi"] == "Thứ Tư"
    assert info["cron"] == "0 17 * * 3"
    assert info["next_run_at"].weekday() == 2  # Wednesday
    assert info["next_run_at"].hour == 17
    assert info["next_run_at"].minute == 0
    assert isinstance(info["scheduler_configured"], bool)


def run_tests() -> None:
    test_next_wednesday_from_monday()
    test_next_wednesday_same_day_before_17()
    test_next_wednesday_same_day_after_17()
    test_next_wednesday_from_thursday()
    test_schedule_info_has_wednesday_fields()
    print("OK: wednesday scheduler tests passed")


if __name__ == "__main__":
    run_tests()
