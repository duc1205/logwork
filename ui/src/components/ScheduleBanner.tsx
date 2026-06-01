import type { ScheduleInfo } from "../api/types";
import { fmtNextRun } from "../utils/datetime";

interface ScheduleBannerProps {
  schedule: ScheduleInfo;
}

export function ScheduleBanner({ schedule }: ScheduleBannerProps) {
  return (
    <div className="schedule-banner">
      <span>📅 Job nhắc — 17:00 {schedule.day_of_week_vi}</span>
      <strong>{fmtNextRun(schedule.next_run_at)}</strong>
      {!schedule.scheduler_enabled && schedule.scheduler_configured && (
        <small className="muted">Scheduler tắt trên server</small>
      )}
    </div>
  );
}
