"""Engine đối soát logwork — Lớp 1 (theo ngày) + Lớp 2 (bù trừ)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Iterable

from .compensation import CompensationPair, detect_compensation
from .models import (
    DailyAudit,
    Discrepancy,
    DiscrepancyType,
    Employee,
    EmployeeLeave,
    EmployeeWeeklySummary,
    Holiday,
    OtRules,
    OvertimeRecord,
    OvertimeStatus,
    TimesheetEntry,
    WeeklyReport,
)
from .note_generator import generate_employee_note
from .penalty import calculate_penalty
from .period_utils import month_range, week_range


def _week_range(anchor: date) -> tuple[date, date]:
    return week_range(anchor)


def _is_weekend(d: date) -> bool:
    return d.weekday() >= 5


class ReconciliationEngine:
    """Đối soát 2 lớp: theo ngày + phát hiện bù trừ."""

    def __init__(
        self,
        *,
        count_weekends: bool = False,
        tolerance_hours: float = 0.25,
        min_hours: float = 8.0,
        max_hours: float = 8.0,
        compensation_threshold: float = 2.0,
        penalty_per_md: float = 20_000,
        ot_rules: OtRules | None = None,
    ):
        self.ot_rules = ot_rules or OtRules()
        self.count_weekends = count_weekends or self.ot_rules.allow_weekend_logging
        self.tolerance_hours = tolerance_hours
        self.min_hours = min_hours
        self.max_hours = max_hours
        self.compensation_threshold = compensation_threshold
        self.penalty_per_md = penalty_per_md

    def working_days(
        self,
        period_start: date,
        period_end: date,
        holidays: Iterable[Holiday],
    ) -> list[date]:
        holiday_dates = {h.holiday_date for h in holidays if h.is_company_wide}
        days: list[date] = []
        current = period_start
        while current <= period_end:
            if current in holiday_dates:
                current += timedelta(days=1)
                continue
            if not self.count_weekends and _is_weekend(current):
                current += timedelta(days=1)
                continue
            days.append(current)
            current += timedelta(days=1)
        return days

    def aggregate_hours(
        self,
        entries: Iterable[TimesheetEntry],
    ) -> dict[tuple[str, date], float]:
        totals: dict[tuple[str, date], float] = defaultdict(float)
        for e in entries:
            totals[(e.employee_id, e.work_date)] += e.hours
        return totals

    def _leave_map(
        self, leaves: list[EmployeeLeave]
    ) -> dict[tuple[str, date], EmployeeLeave]:
        return {(lv.employee_id, lv.leave_date): lv for lv in leaves}

    def _ot_map(
        self, overtime: list[OvertimeRecord]
    ) -> dict[tuple[str, date], float]:
        result: dict[tuple[str, date], float] = {}
        rules = self.ot_rules
        for ot in overtime:
            ok = (
                (ot.status == OvertimeStatus.APPROVED and rules.accept_approved)
                or (ot.status == OvertimeStatus.PENDING and rules.accept_pending)
            )
            if not ok:
                continue
            key = (ot.employee_id, ot.ot_date)
            result[key] = result.get(key, 0.0) + ot.ot_hours
        return result

    def _required_hours(
        self,
        emp: Employee,
        *,
        is_holiday: bool,
        is_leave: bool,
    ) -> float:
        if is_holiday or is_leave:
            return 0.0
        return emp.expected_hours_per_day

    def _valid_max_hours(self, ot_hours: float) -> float:
        rules = self.ot_rules
        capped_ot = min(max(ot_hours, 0.0), rules.max_ot_hours_per_day)
        base = self.min_hours + capped_ot + rules.ot_grace_hours
        return min(base, rules.max_daily_hours)

    def _detect_compensation_for_audits(
        self,
        employee_id: str,
        daily_audits: list[DailyAudit],
        *,
        split_by_week: bool,
    ) -> list[CompensationPair]:
        if not split_by_week:
            return detect_compensation(
                employee_id,
                daily_audits,
                min_hours=self.min_hours,
                max_hours=self.max_hours,
                tolerance_hours=self.tolerance_hours,
                compensation_threshold=self.compensation_threshold,
            )

        pairs: list[CompensationPair] = []
        by_week: dict[date, list[DailyAudit]] = defaultdict(list)
        for audit in daily_audits:
            ws = audit.work_date - timedelta(days=audit.work_date.weekday())
            by_week[ws].append(audit)
        for week_audits in by_week.values():
            pairs.extend(
                detect_compensation(
                    employee_id,
                    week_audits,
                    min_hours=self.min_hours,
                    max_hours=self.max_hours,
                    tolerance_hours=self.tolerance_hours,
                    compensation_threshold=self.compensation_threshold,
                )
            )
        return pairs

    def reconcile_period(
        self,
        *,
        period_start: date,
        period_end: date,
        employees: list[Employee],
        entries: list[TimesheetEntry],
        holidays: list[Holiday],
        leaves: list[EmployeeLeave] | None = None,
        overtime: list[OvertimeRecord] | None = None,
        use_monthly_target: bool = False,
        compensation_by_week: bool = False,
    ) -> WeeklyReport:
        working = self.working_days(period_start, period_end, holidays)
        holiday_dates = {h.holiday_date for h in holidays if h.is_company_wide}
        totals = self.aggregate_hours(entries)
        leave_map = self._leave_map(leaves or [])
        ot_map = self._ot_map(overtime or [])

        discrepancies: list[Discrepancy] = []
        summaries: list[EmployeeWeeklySummary] = []
        total_penalty = 0

        for emp in employees:
            daily_audits: list[DailyAudit] = []
            emp_discrepancies: list[Discrepancy] = []
            holiday_count = 0

            for day in working:
                is_holiday = day in holiday_dates
                is_leave = (emp.account_id, day) in leave_map
                if is_holiday:
                    holiday_count += 1

                required = self._required_hours(
                    emp, is_holiday=is_holiday, is_leave=is_leave
                )
                actual = totals.get((emp.account_id, day), 0.0)
                ot_hours = ot_map.get((emp.account_id, day), 0.0)
                valid_max = self._valid_max_hours(ot_hours)

                missed = 0.0
                day_penalty = 0

                if required > 0:
                    if actual < required - self.tolerance_hours:
                        missed = required - actual
                        day_penalty = calculate_penalty(
                            missed, penalty_per_md=self.penalty_per_md
                        )
                        dtype = (
                            DiscrepancyType.MISSING_DAY
                            if actual <= self.tolerance_hours
                            else DiscrepancyType.UNDER_HOURS
                        )
                        disc = Discrepancy(
                            employee_id=emp.account_id,
                            work_date=day,
                            discrepancy_type=dtype,
                            expected_hours=required,
                            actual_hours=actual,
                            delta_hours=missed,
                            penalty=day_penalty,
                            message=(
                                f"{emp.display_name}: thiếu {missed:.1f}h "
                                f"ngày {day.isoformat()}"
                            ),
                        )
                        emp_discrepancies.append(disc)
                        discrepancies.append(disc)
                    elif actual > valid_max + self.tolerance_hours:
                        over = actual - valid_max
                        disc = Discrepancy(
                            employee_id=emp.account_id,
                            work_date=day,
                            discrepancy_type=DiscrepancyType.OVER_HOURS,
                            expected_hours=valid_max,
                            actual_hours=actual,
                            delta_hours=over,
                            message=(
                                f"{emp.display_name}: vượt {over:.1f}h "
                                f"ngày {day.isoformat()}"
                            ),
                        )
                        emp_discrepancies.append(disc)
                        discrepancies.append(disc)

                daily_audits.append(
                    DailyAudit(
                        employee_id=emp.account_id,
                        work_date=day,
                        required_hours=required,
                        actual_hours=actual,
                        missed_hours=missed,
                        penalty=day_penalty,
                        is_holiday=is_holiday,
                        is_leave=is_leave,
                        ot_hours=ot_hours,
                    )
                )

            comp_pairs = self._detect_compensation_for_audits(
                emp.account_id,
                daily_audits,
                split_by_week=compensation_by_week,
            )
            for pair in comp_pairs:
                comp_disc = Discrepancy(
                    employee_id=emp.account_id,
                    work_date=pair.under_day,
                    discrepancy_type=DiscrepancyType.COMPENSATION,
                    expected_hours=self.min_hours,
                    actual_hours=0,
                    delta_hours=pair.under_hours,
                    message=pair.message,
                )
                emp_discrepancies.append(comp_disc)
                discrepancies.append(comp_disc)

            for (eid, day), hours in totals.items():
                if eid != emp.account_id or hours <= 0:
                    continue
                if day < period_start or day > period_end:
                    continue
                if day in holiday_dates:
                    if not self.ot_rules.allow_holiday_logging:
                        discrepancies.append(
                            Discrepancy(
                                employee_id=eid,
                                work_date=day,
                                discrepancy_type=DiscrepancyType.HOLIDAY_LOGGED,
                                expected_hours=0,
                                actual_hours=hours,
                                delta_hours=hours,
                                message=f"Log {hours:.1f}h trên ngày nghỉ {day.isoformat()}",
                            )
                        )
                elif (eid, day) in leave_map:
                    if not self.ot_rules.allow_leave_logging:
                        discrepancies.append(
                            Discrepancy(
                                employee_id=eid,
                                work_date=day,
                                discrepancy_type=DiscrepancyType.LEAVE_VIOLATION,
                                expected_hours=0,
                                actual_hours=hours,
                                delta_hours=hours,
                                message=f"Log {hours:.1f}h trên ngày phép {day.isoformat()}",
                            )
                        )
                elif not self.count_weekends and _is_weekend(day):
                    if not self.ot_rules.allow_weekend_logging:
                        discrepancies.append(
                            Discrepancy(
                                employee_id=eid,
                                work_date=day,
                                discrepancy_type=DiscrepancyType.WEEKEND_LOGGED,
                                expected_hours=0,
                                actual_hours=hours,
                                delta_hours=hours,
                                message=f"Log {hours:.1f}h cuối tuần {day.isoformat()}",
                            )
                        )

            emp_penalty = sum(a.penalty for a in daily_audits)
            total_penalty += emp_penalty

            if use_monthly_target and emp.target_md_month is not None:
                target_md = emp.target_md_month
            elif use_monthly_target:
                target_md = float(len(working) - holiday_count)
            else:
                target_md = emp.target_md_week or float(len(working) - holiday_count)

            note = generate_employee_note(
                daily_audits, emp_discrepancies, comp_pairs
            )

            summaries.append(
                EmployeeWeeklySummary(
                    employee_id=emp.account_id,
                    display_name=emp.display_name,
                    holiday_count=holiday_count,
                    actual_hours=sum(a.actual_hours for a in daily_audits),
                    required_hours=sum(a.required_hours for a in daily_audits),
                    missed_hours=sum(a.missed_hours for a in daily_audits),
                    penalty=emp_penalty,
                    target_md=target_md,
                    note=note,
                    daily_audits=daily_audits,
                    compensation_pairs=comp_pairs,
                )
            )

        return WeeklyReport(
            week_start=period_start,
            week_end=period_end,
            discrepancies=discrepancies,
            employees_checked=len(employees),
            working_days=working,
            summaries=summaries,
            total_penalty=total_penalty,
        )

    def reconcile_week(
        self,
        *,
        anchor_date: date,
        employees: list[Employee],
        entries: list[TimesheetEntry],
        holidays: list[Holiday],
        leaves: list[EmployeeLeave] | None = None,
        overtime: list[OvertimeRecord] | None = None,
    ) -> WeeklyReport:
        start, end = week_range(anchor_date)
        return self.reconcile_period(
            period_start=start,
            period_end=end,
            employees=employees,
            entries=entries,
            holidays=holidays,
            leaves=leaves,
            overtime=overtime,
        )

    def reconcile_month(
        self,
        *,
        year: int,
        month: int,
        employees: list[Employee],
        entries: list[TimesheetEntry],
        holidays: list[Holiday],
        leaves: list[EmployeeLeave] | None = None,
        overtime: list[OvertimeRecord] | None = None,
    ) -> WeeklyReport:
        start, end = month_range(year, month)
        return self.reconcile_period(
            period_start=start,
            period_end=end,
            employees=employees,
            entries=entries,
            holidays=holidays,
            leaves=leaves,
            overtime=overtime,
            use_monthly_target=True,
            compensation_by_week=True,
        )
