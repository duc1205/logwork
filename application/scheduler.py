"""Lịch chạy hệ thống."""



from __future__ import annotations



from dataclasses import dataclass

from datetime import date, datetime, timedelta

from enum import Enum

from pathlib import Path



from ..paths import MOCK_DIR, OUTPUT_DIR
from ..domain.period_utils import parse_month

from .pipeline import run_month, run_week





class JobType(str, Enum):

    PREDICTIVE = "predictive"

    REMINDER = "reminder"

    WEEKLY_CLOSE = "weekly_close"

    MONTHLY_CLOSE = "monthly_close"





@dataclass(frozen=True)

class ScheduledJob:

    job_type: JobType

    cron_hint: str

    description: str





SCHEDULE: list[ScheduledJob] = [

    ScheduledJob(JobType.PREDICTIVE, "Tue-Wed 14:00", "Canh bao som pace tuan"),

    ScheduledJob(JobType.REMINDER, "Wed-Thu 09:00", "Nhac NV thieu log"),

    ScheduledJob(JobType.WEEKLY_CLOSE, "Fri 09:00", "Chot tuan + bao cao + phat"),

    ScheduledJob(JobType.MONTHLY_CLOSE, "Day-3 17:00", "Chot bao cao thang"),

]





def _predictive_as_of(anchor: date) -> date:

    """Mặc định: thứ T4 của tuần anchor (demo predictive)."""

    week_start = anchor - timedelta(days=anchor.weekday())

    return week_start + timedelta(days=2)





def _resolve_monthly_period(

    *,

    anchor_date: date | None,

    month: str | None,

    data_dir: Path,

) -> tuple[int, int]:

    if month:

        return parse_month(month)

    ref = anchor_date

    if ref is None:

        import json



        cfg = json.loads((data_dir / "config.json").read_text(encoding="utf-8"))

        ref = date.fromisoformat(cfg["anchor_date"])

    return ref.year, ref.month





def run_job(

    job_type: JobType,

    *,

    anchor_date: date | None = None,

    month: str | None = None,

    data_dir: Path | None = None,

    output_dir: Path | None = None,

    use_live_jira: bool = False,

) -> Path:

    out = output_dir or OUTPUT_DIR

    out.mkdir(parents=True, exist_ok=True)

    directory = data_dir or MOCK_DIR



    if job_type == JobType.MONTHLY_CLOSE:

        year, mon = _resolve_monthly_period(

            anchor_date=anchor_date, month=month, data_dir=directory

        )

        report, paths = run_month(

            year=year,

            month=mon,

            data_dir=directory,

            output_dir=out,

            export_heatmap=True,

            send_reminders=True,

            use_live_jira=use_live_jira,

        )

        period_label = f"{year}-{mon:02d}"

    else:

        kwargs: dict = {

            "anchor_date": anchor_date,

            "data_dir": directory,

            "output_dir": out,

            "use_live_jira": use_live_jira,

        }



        if job_type == JobType.PREDICTIVE:

            kwargs["run_predictive"] = True

            kwargs["export_heatmap"] = True

            if anchor_date:

                kwargs["predictive_as_of"] = _predictive_as_of(anchor_date)

        elif job_type in (JobType.REMINDER, JobType.WEEKLY_CLOSE):

            kwargs["send_reminders"] = True

            kwargs["export_heatmap"] = job_type == JobType.WEEKLY_CLOSE



        report, paths = run_week(**kwargs)

        period_label = f"{report.week_start}..{report.week_end}"



    log_path = out / f"scheduler_{job_type.value}_{datetime.now():%Y%m%d_%H%M%S}.log"

    lines = [

        f"job={job_type.value}",

        f"ran_at={datetime.now().isoformat()}",

        f"period={period_label}",

        f"employees={report.employees_checked}",

        f"penalty={report.total_penalty}",

    ]

    for key, p in paths.items():

        lines.append(f"{key}={p}")

    log_path.write_text("\n".join(lines), encoding="utf-8")

    return log_path


