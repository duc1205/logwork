/** Định dạng ngày giờ hiển thị UI (vi-VN). */

export function fmtNextRun(iso: string): string {
  return new Date(iso).toLocaleString("vi-VN", {
    weekday: "long",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function fmtDateViShort(iso: string): string {
  return new Date(iso + "T12:00:00").toLocaleDateString("vi-VN", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}
