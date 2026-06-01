/** Tiện ích chọn tuần ISO (T2→CN). */

export function todayIso(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function addDays(iso: string, delta: number): string {
  const d = new Date(iso + "T12:00:00");
  d.setDate(d.getDate() + delta);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function addWeeks(iso: string, weeks: number): string {
  return addDays(iso, weeks * 7);
}

/** Thứ 2 của tuần chứa ngày iso. */
export function weekStart(iso: string): string {
  const d = new Date(iso + "T12:00:00");
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${dd}`;
}

export function fmtRangeVi(start: string, end: string): string {
  const s = new Date(start + "T00:00:00").toLocaleDateString("vi-VN");
  const e = new Date(end + "T00:00:00").toLocaleDateString("vi-VN");
  return `${s} → ${e}`;
}

export function fmtDateVi(iso: string): string {
  return new Date(iso + "T00:00:00").toLocaleDateString("vi-VN");
}
