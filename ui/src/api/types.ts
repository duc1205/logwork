export interface UserInfo {
  account_id: string;
  display_name: string;
  email: string;
  team: string | null;
  center: string | null;
  role: "employee" | "qa" | "admin";
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export interface DailyAuditItem {
  work_date: string;
  required_hours: number;
  actual_hours: number;
  missed_hours: number;
  penalty: number;
  is_holiday: boolean;
  is_leave: boolean;
}

export interface CompensationItem {
  under_day: string;
  over_day: string;
  under_hours: number;
  over_hours: number;
  confidence: string;
  message: string;
}

export interface WeeklySummary {
  week_start: string;
  week_end: string;
  as_of: string;
  period_mode?: "week" | "month";
  data_source: string;
  display_name: string;
  account_id: string;
  holiday_count: number;
  actual_hours: number;
  required_hours: number;
  missed_hours: number;
  penalty: number;
  target_md: number;
  note: string;
  daily_audits: DailyAuditItem[];
  compensation_pairs?: CompensationItem[];
}

export interface HeatmapCell {
  employee_id: string;
  display_name: string;
  date: string;
  actual: number;
  required: number;
  status: string;
  color: string;
  penalty: number;
  is_leave: boolean;
  is_holiday: boolean;
}

export interface HeatmapData {
  week_start: string;
  week_end: string;
  as_of: string;
  period_mode?: "week" | "month";
  data_source: string;
  cells: HeatmapCell[];
}

export interface NotificationItem {
  id: string;
  employee_id: string;
  display_name: string;
  subject: string;
  body: string;
  channel: string;
  recipient_email?: string | null;
  work_date: string | null;
  discrepancy_type: string | null;
  created_at: string;
}

export interface NotificationList {
  week_start: string;
  week_end: string;
  generated_at: string | null;
  data_source?: string | null;
  schedule_hint: string;
  total: number;
  items: NotificationItem[];
}

export interface ScheduleInfo {
  wednesday_reminder: string;
  next_run_at: string;
  timezone: string;
  cron: string;
  day_of_week: string;
  day_of_week_vi: string;
  scheduler_enabled: boolean;
  scheduler_configured: boolean;
  credentials_configured: boolean;
  last_run_at: string | null;
  last_run_ok: boolean | null;
  schedule_hint: string;
}

export interface PredictiveAlert {
  employee_id: string;
  display_name: string;
  alert_type: string;
  message: string;
}

export interface PredictiveData {
  week_start: string;
  week_end: string;
  as_of: string;
  period_mode?: string;
  data_source: string;
  total: number;
  items: PredictiveAlert[];
  hint: string;
}

export interface GoldenCompareRow {
  account: string;
  engine_missed_md: number | null;
  golden_missed_md: number | null;
  engine_penalty: number | null;
  golden_penalty: number | null;
  status: "ok" | "error" | "warning";
}

export interface GoldenCompareResult {
  week_start: string;
  week_end: string;
  period_mode: string;
  data_source: string;
  golden_rows: number;
  engine_rows: number;
  matched: number;
  errors: string[];
  warnings: string[];
  ok: boolean;
  rows: GoldenCompareRow[];
}

export interface JiraAccountOption {
  account_id: string;
  display_name: string;
  jira_user_id?: string;
  source?: "jira" | "roster";
}

export interface AuditSettings {
  min_hours: number;
  max_hours: number;
  tolerance_hours: number;
  penalty_per_md: number;
  compensation_threshold: number;
  predictive_tue_pace_min: number;
  predictive_wed_pace_min: number;
  ot_rules: OtRules;
  data_dir: string;
  note?: string | null;
}

export interface OtRules {
  max_ot_hours_per_day: number;
  max_daily_hours: number;
  ot_grace_hours: number;
  accept_approved: boolean;
  accept_pending: boolean;
  allow_weekend_logging: boolean;
  allow_holiday_logging: boolean;
  allow_leave_logging: boolean;
  valid_max_formula?: string;
}

export interface OvertimeItem {
  employee_id: string;
  display_name?: string | null;
  ot_date: string;
  ot_hours: number;
  reason: string;
  status: string;
  approved_by?: string | null;
}

export interface OvertimeList {
  total: number;
  items: OvertimeItem[];
}

export interface HolidayItem {
  holiday_date: string;
  name: string;
  is_company_wide: boolean;
}

export interface HolidaysList {
  total: number;
  items: HolidayItem[];
}
