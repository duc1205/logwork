/** Tiện ích chọn kỳ — tuần ISO (T2→CN) và tháng calendar. */

export type PeriodMode = "week" | "month";

export interface PeriodSelection {
  mode: PeriodMode;
  /** Tuần: YYYY-MM-DD (T2) */
  start: string;
  /** Tuần: YYYY-MM-DD (CN) */
  end: string;
  /** Tháng: YYYY-MM */
  month: string;
}

export function todayIso(): string {
  const d = new Date();
  return toIso(d);
}

function toIso(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function addDays(iso: string, delta: number): string {
  const d = new Date(iso + "T12:00:00");
  d.setDate(d.getDate() + delta);
  return toIso(d);
}

/** Thứ 2 của tuần chứa ngày iso. */
export function weekStart(iso: string): string {
  const d = new Date(iso + "T12:00:00");
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  return toIso(d);
}

/** Chủ nhật của tuần chứa ngày iso. */
export function weekEnd(iso: string): string {
  return addDays(weekStart(iso), 6);
}

export function weekRange(iso: string): { start: string; end: string } {
  const start = weekStart(iso);
  return { start, end: addDays(start, 6) };
}

export function currentMonth(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export function monthRange(ym: string): { start: string; end: string } {
  const [y, m] = ym.split("-").map(Number);
  const last = new Date(y, m, 0).getDate();
  return {
    start: `${y}-${String(m).padStart(2, "0")}-01`,
    end: `${y}-${String(m).padStart(2, "0")}-${String(last).padStart(2, "0")}`,
  };
}

export function addMonths(ym: string, delta: number): string {
  const [y, m] = ym.split("-").map(Number);
  const d = new Date(y, m - 1 + delta, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export function defaultPeriod(): PeriodSelection {
  const today = todayIso();
  const { start, end } = weekRange(today);
  return { mode: "week", start, end, month: currentMonth() };
}

export function periodBounds(p: PeriodSelection): { start: string; end: string } {
  if (p.mode === "month") return monthRange(p.month);
  return { start: p.start, end: p.end };
}

export function periodQueryString(p: PeriodSelection): string {
  if (p.mode === "month") return `month=${p.month}`;
  return `start=${p.start}&end=${p.end}`;
}

export function fmtRangeVi(start: string, end: string): string {
  const s = new Date(start + "T00:00:00").toLocaleDateString("vi-VN");
  const e = new Date(end + "T00:00:00").toLocaleDateString("vi-VN");
  return `${s} → ${e}`;
}

export function fmtDateVi(iso: string): string {
  return new Date(iso + "T00:00:00").toLocaleDateString("vi-VN");
}

export function canGoNextPeriod(p: PeriodSelection): boolean {
  if (p.mode === "month") return p.month < currentMonth();
  const { end } = periodBounds(p);
  return end < todayIso();
}
