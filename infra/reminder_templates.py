"""Template nhắc nhở Teams/email (rule-based)."""

from __future__ import annotations

from ..domain.models import Discrepancy, DiscrepancyType


def build_reminder(d: Discrepancy, employee_name: str) -> str:
    """Sinh nội dung nhắc từ Discrepancy."""

    day_str = d.work_date.strftime("%d/%m/%Y")
    if d.discrepancy_type in (DiscrepancyType.MISSING_DAY, DiscrepancyType.UNDER_HOURS):
        return (
            f"Chào {employee_name},\n"
            f"Vui lòng kiểm tra logwork ngày {day_str}: "
            f"bạn đang thiếu {d.delta_hours:.1f} giờ "
            f"(đã log {d.actual_hours:.1f}h / chuẩn {d.expected_hours:.1f}h).\n"
            f"Cập nhật trên Jira trước cuối ngày hôm nay. Cảm ơn!"
        )
    if d.discrepancy_type == DiscrepancyType.OVER_HOURS:
        return (
            f"Chào {employee_name},\n"
            f"Ngày {day_str} bạn log {d.actual_hours:.1f}h, "
            f"vượt chuẩn {d.expected_hours:.1f}h ({d.delta_hours:.1f}h). "
            f"Vui lòng rà soát lại timesheet."
        )
    if d.discrepancy_type == DiscrepancyType.HOLIDAY_LOGGED:
        return (
            f"Chào {employee_name},\n"
            f"Ngày {day_str} là ngày nghỉ nhưng có {d.actual_hours:.1f}h logwork. "
            f"Kiểm tra lại ticket/ngày log."
        )
    if d.discrepancy_type == DiscrepancyType.COMPENSATION:
        return (
            f"Chào {employee_name},\n"
            f"Phát hiện bù trừ giờ trong tuần: {d.message}\n"
            f"Vui lòng rà soát và điều chỉnh worklog trên Jira."
        )
    return f"Chào {employee_name},\n{d.message}"
