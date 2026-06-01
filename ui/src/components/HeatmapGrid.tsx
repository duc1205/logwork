import type { HeatmapCell } from "../api/types";

const COLOR_CLASS: Record<string, string> = {
  green: "hm-green",
  lightgreen: "hm-lightgreen",
  yellow: "hm-yellow",
  orange: "hm-orange",
  red: "hm-red",
  purple: "hm-purple",
  gray: "hm-gray",
};

function fmtDay(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("vi-VN", { weekday: "short", day: "2-digit", month: "2-digit" });
}

function fmtShort(iso: string): string {
  return iso.slice(8, 10) + "/" + iso.slice(5, 7);
}

interface Props {
  cells: HeatmapCell[];
  onCellClick?: (employeeId: string, date: string) => void;
}

export function HeatmapGrid({ cells, onCellClick }: Props) {
  if (cells.length === 0) {
    return <p className="muted">Không có dữ liệu heatmap cho kỳ này.</p>;
  }

  const dates = [...new Set(cells.map((c) => c.date))].sort();
  const employees: { id: string; name: string; map: Map<string, HeatmapCell> }[] = [];
  const byEmp = new Map<string, { id: string; name: string; map: Map<string, HeatmapCell> }>();

  for (const cell of cells) {
    if (!byEmp.has(cell.employee_id)) {
      const emp = { id: cell.employee_id, name: cell.display_name, map: new Map<string, HeatmapCell>() };
      byEmp.set(cell.employee_id, emp);
      employees.push(emp);
    }
    byEmp.get(cell.employee_id)!.map.set(cell.date, cell);
  }
  employees.sort((a, b) => a.name.localeCompare(b.name, "vi"));

  return (
    <div className="heatmap-wrap">
      <div className="heatmap-legend">
        <span><i className="hm-swatch hm-green" /> OK</span>
        <span><i className="hm-swatch hm-lightgreen" /> Đủ nhẹ</span>
        <span><i className="hm-swatch hm-yellow" /> Thiếu nhẹ</span>
        <span><i className="hm-swatch hm-orange" /> Thiếu vừa</span>
        <span><i className="hm-swatch hm-red" /> Không log</span>
        <span><i className="hm-swatch hm-purple" /> Bù trừ</span>
        <span><i className="hm-swatch hm-gray" /> Nghỉ / lễ</span>
      </div>
      {onCellClick && (
        <p className="muted heatmap-hint">Nhấn ô để xem chi tiết NV trên Dashboard.</p>
      )}
      <div className="table-wrap heatmap-scroll">
        <table className="data-table heatmap-table">
          <thead>
            <tr>
              <th className="hm-sticky-col">Nhân viên</th>
              {dates.map((d) => (
                <th key={d} title={d}>
                  {fmtShort(d)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {employees.map((emp) => (
              <tr key={emp.id}>
                <td className="hm-sticky-col hm-name" title={`${emp.name} (@${emp.id})`}>
                  <strong>{emp.name}</strong>
                  <small>@{emp.id}</small>
                </td>
                {dates.map((d) => {
                  const cell = emp.map.get(d);
                  if (!cell) {
                    return (
                      <td key={d} className="hm-cell empty">
                        —
                      </td>
                    );
                  }
                  const cls = COLOR_CLASS[cell.color] ?? "hm-gray";
                  const title = `${fmtDay(d)}: ${cell.actual}h / ${cell.required}h (${cell.status})`;
                  const content = cell.actual > 0 ? cell.actual.toFixed(0) : "·";
                  return (
                    <td key={d} className="hm-cell">
                      {onCellClick ? (
                        <button
                          type="button"
                          className={`hm-block hm-clickable ${cls}`}
                          title={title}
                          onClick={() => onCellClick(emp.id, d)}
                        >
                          {content}
                        </button>
                      ) : (
                        <span className={`hm-block ${cls}`} title={title}>
                          {content}
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
