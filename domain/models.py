"""Data models cho pipeline đối soát logwork."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .compensation import CompensationPair


class DiscrepancyType(str, Enum):
    MISSING_DAY = "missing_day"
    UNDER_HOURS = "under_hours"
    OVER_HOURS = "over_hours"
    HOLIDAY_LOGGED = "holiday_logged"
    WEEKEND_LOGGED = "weekend_logged"
    COMPENSATION = "compensation"
    LEAVE_VIOLATION = "leave_violation"


class LeaveType(str, Enum):
    ANNUAL = "annual"
    SICK = "sick"
    UNPAID = "unpaid"
    OTHER = "other"


class OvertimeStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Employee:
    account_id: str
    display_name: str
    email: str
    team: Optional[str] = None
    center: Optional[str] = None
    expected_hours_per_day: float = 8.0
    target_md_week: Optional[float] = None
    target_md_month: Optional[float] = None


@dataclass(frozen=True)
class TimesheetEntry:
    employee_id: str
    work_date: date
    hours: float
    issue_key: Optional[str] = None
    project_key: Optional[str] = None


@dataclass(frozen=True)
class Holiday:
    holiday_date: date
    name: str
    is_company_wide: bool = True


@dataclass(frozen=True)
class EmployeeLeave:
    employee_id: str
    leave_date: date
    leave_type: LeaveType = LeaveType.ANNUAL
    source: str = "excel"


@dataclass(frozen=True)
class OvertimeRecord:
    employee_id: str
    ot_date: date
    ot_hours: float
    reason: str = ""
    status: OvertimeStatus = OvertimeStatus.PENDING
    approved_by: Optional[str] = None


@dataclass
class Discrepancy:
    employee_id: str
    work_date: date
    discrepancy_type: DiscrepancyType
    expected_hours: float
    actual_hours: float
    delta_hours: float
    message: str
    penalty: int = 0


@dataclass
class DailyAudit:
    employee_id: str
    work_date: date
    required_hours: float
    actual_hours: float
    missed_hours: float
    penalty: int
    is_holiday: bool = False
    is_leave: bool = False
    ot_hours: float = 0.0


@dataclass
class EmployeeWeeklySummary:
    employee_id: str
    display_name: str
    holiday_count: int
    actual_hours: float
    required_hours: float
    missed_hours: float
    penalty: int
    target_md: float
    note: str
    daily_audits: list[DailyAudit] = field(default_factory=list)
    compensation_pairs: list["CompensationPair"] = field(default_factory=list)


@dataclass
class WeeklyReport:
    week_start: date
    week_end: date
    discrepancies: list[Discrepancy] = field(default_factory=list)
    employees_checked: int = 0
    working_days: list[date] = field(default_factory=list)
    summaries: list[EmployeeWeeklySummary] = field(default_factory=list)
    total_penalty: int = 0


@dataclass(frozen=True)
class OtRules:
    """Quy tắc chấp nhận logwork ngoài giờ / ngoài ngày làm việc."""

    max_ot_hours_per_day: float = 4.0
    max_daily_hours: float = 12.0
    ot_grace_hours: float = 0.0
    accept_approved: bool = True
    accept_pending: bool = False
    allow_weekend_logging: bool = False
    allow_holiday_logging: bool = False
    allow_leave_logging: bool = False


@dataclass(frozen=True)
class AuditConfig:
    min_hours: float = 8.0
    max_hours: float = 8.0
    tolerance_hours: float = 0.25
    penalty_per_md: float = 20_000
    compensation_threshold: float = 2.0
    project_keys: tuple[str, ...] = ()
    predictive_tue_pace_min: float = 0.20
    predictive_wed_pace_min: float = 0.40
    ot_rules: OtRules = OtRules()
