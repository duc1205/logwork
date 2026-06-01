import type { DailyAuditItem } from "../api/types";

function fmtDate(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("vi-VN", { weekday: "short", day: "2-digit", month: "2-digit" });
}

function statusClass(row: DailyAuditItem): string {
  if (row.is_holiday) return "row-holiday";
  if (row.is_leave) return "row-leave";
  if (row.missed_hours > 0) return "row-miss";
  return "row-ok";
}

export function DailyTable({ rows }: { rows: DailyAuditItem[] }) {
  if (rows.length === 0) {
    return <p className="muted">Không có dữ liệu ngày trong tuần.</p>;
  }

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Ngày</th>
            <th>Chuẩn (h)</th>
            <th>Thực tế (h)</th>
            <th>Thiếu (h)</th>
            <th>Phạt (VND)</th>
            <th>Trạng thái</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.work_date} className={statusClass(r)}>
              <td>{fmtDate(r.work_date)}</td>
              <td>{r.required_hours.toFixed(1)}</td>
              <td>{r.actual_hours.toFixed(1)}</td>
              <td>{r.missed_hours > 0 ? r.missed_hours.toFixed(1) : "—"}</td>
              <td>{r.penalty > 0 ? r.penalty.toLocaleString("vi-VN") : "—"}</td>
              <td>
                {r.is_holiday && <span className="badge badge-blue">Lễ</span>}
                {r.is_leave && <span className="badge badge-purple">Phép</span>}
                {!r.is_holiday && !r.is_leave && r.missed_hours <= 0 && (
                  <span className="badge badge-green">OK</span>
                )}
                {!r.is_holiday && !r.is_leave && r.missed_hours > 0 && (
                  <span className="badge badge-red">Thiếu</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
