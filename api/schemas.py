"""Pydantic schemas cho REST API."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, description="Jira username (account_id)")
    password: str = Field(min_length=1)


class UserInfo(BaseModel):
    account_id: str
    display_name: str
    email: str = ""
    team: str | None = None
    center: str | None = None
    role: str = "employee"  # employee | qa | admin


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class DailyAuditItem(BaseModel):
    work_date: date
    required_hours: float
    actual_hours: float
    missed_hours: float
    penalty: int
    is_holiday: bool = False
    is_leave: bool = False


class CompensationItem(BaseModel):
    under_day: date
    over_day: date
    under_hours: float
    over_hours: float
    confidence: str
    message: str


class WeeklySummaryResponse(BaseModel):
    week_start: date
    week_end: date
    as_of: date = Field(description="Chỉ tính/hiển thị ngày làm việc đến ngày này")
    period_mode: str = Field(default="week", description="week | month")
    data_source: str = Field(
        default="plugin",
        description="plugin | plugin_team (chỉ Jira live)",
    )
    display_name: str
    account_id: str
    holiday_count: int
    actual_hours: float
    required_hours: float
    missed_hours: float
    penalty: int
    target_md: float
    note: str
    daily_audits: list[DailyAuditItem]
    compensation_pairs: list[CompensationItem] = Field(default_factory=list)


class HeatmapCell(BaseModel):
    employee_id: str
    display_name: str
    date: date
    actual: float
    required: float
    status: str
    color: str
    penalty: int
    is_leave: bool = False
    is_holiday: bool = False


class HeatmapResponse(BaseModel):
    week_start: date
    week_end: date
    as_of: date
    period_mode: str = "week"
    data_source: str = "plugin"
    cells: list[HeatmapCell]


class NotificationItem(BaseModel):
    id: str
    employee_id: str
    display_name: str
    subject: str
    body: str
    channel: str = "app"
    recipient_email: str | None = None
    work_date: date | None = None
    discrepancy_type: str | None = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    week_start: date
    week_end: date
    generated_at: datetime | None = None
    data_source: str | None = None
    schedule_hint: str = "Mỗi 17:00 thứ Tư hàng tuần"
    total: int
    items: list[NotificationItem]


class ScheduleInfoResponse(BaseModel):
    wednesday_reminder: str
    next_run_at: datetime
    timezone: str = "Asia/Ho_Chi_Minh"
    cron: str = "0 17 * * 3"
    day_of_week: str = "wednesday"
    day_of_week_vi: str = "Thứ Tư"
    scheduler_enabled: bool = False
    scheduler_configured: bool = True
    credentials_configured: bool = False
    last_run_at: datetime | None = None
    last_run_ok: bool | None = None
    schedule_hint: str = "Tự động mỗi 17:00 thứ Tư (Asia/Ho_Chi_Minh)"


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    mode: str = "jira_live"
    data_dir: str = ""
    config_ready: bool = True


class PredictiveAlertItem(BaseModel):
    employee_id: str
    display_name: str
    alert_type: str  # midweek_pace | pattern
    message: str


class PredictiveResponse(BaseModel):
    week_start: date
    week_end: date
    as_of: date
    period_mode: str = "week"
    data_source: str = "plugin"
    total: int
    items: list[PredictiveAlertItem]
    hint: str = ""


class GoldenCompareRow(BaseModel):
    account: str
    engine_missed_md: float | None = None
    golden_missed_md: float | None = None
    engine_penalty: int | None = None
    golden_penalty: int | None = None
    status: str  # ok | error | warning


class GoldenCompareResponse(BaseModel):
    week_start: date
    week_end: date
    period_mode: str
    data_source: str
    golden_rows: int
    engine_rows: int
    matched: int
    errors: list[str]
    warnings: list[str]
    ok: bool
    rows: list[GoldenCompareRow] = Field(default_factory=list)


class AuditSettingsResponse(BaseModel):
    min_hours: float
    max_hours: float
    tolerance_hours: float
    penalty_per_md: int
    compensation_threshold: float
    predictive_tue_pace_min: float = 0.20
    predictive_wed_pace_min: float = 0.40
    ot_rules: "OtRulesResponse"
    data_dir: str = ""
    note: str | None = None


class OtRulesResponse(BaseModel):
    max_ot_hours_per_day: float
    max_daily_hours: float
    ot_grace_hours: float
    accept_approved: bool
    accept_pending: bool
    allow_weekend_logging: bool
    allow_holiday_logging: bool
    allow_leave_logging: bool
    valid_max_formula: str = "min(min_hours + min(OT, max_ot) + grace, max_daily)"


class OtRulesUpdate(BaseModel):
    max_ot_hours_per_day: float | None = Field(None, ge=0)
    max_daily_hours: float | None = Field(None, gt=0)
    ot_grace_hours: float | None = Field(None, ge=0)
    accept_approved: bool | None = None
    accept_pending: bool | None = None
    allow_weekend_logging: bool | None = None
    allow_holiday_logging: bool | None = None
    allow_leave_logging: bool | None = None


class OvertimeItem(BaseModel):
    employee_id: str
    display_name: str | None = None
    ot_date: date
    ot_hours: float
    reason: str = ""
    status: str = "approved"
    approved_by: str | None = None


class OvertimeCreate(BaseModel):
    employee_id: str = Field(min_length=1)
    ot_date: date
    ot_hours: float = Field(gt=0)
    reason: str = ""
    status: str = "approved"
    approved_by: str | None = None


class OvertimeListResponse(BaseModel):
    total: int
    items: list[OvertimeItem]


class AuditSettingsUpdate(BaseModel):
    penalty_per_md: int | None = Field(None, ge=0, description="VNĐ / MD thiếu")
    tolerance_hours: float | None = Field(None, ge=0, description="Sai số giờ cho phép")
    compensation_threshold: float | None = Field(None, gt=0, description="Ngưỡng bù trừ (giờ)")


class HolidayItem(BaseModel):
    holiday_date: date
    name: str
    is_company_wide: bool = True


class HolidayCreate(BaseModel):
    holiday_date: date
    name: str = Field(min_length=1, max_length=200)
    is_company_wide: bool = True


class HolidaysListResponse(BaseModel):
    total: int
    items: list[HolidayItem]
