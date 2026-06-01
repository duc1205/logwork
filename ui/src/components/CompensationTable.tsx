import type { CompensationItem } from "../api/types";
import { fmtDateVi } from "../utils/period";

const CONF_LABEL: Record<string, string> = {
  high: "Cao",
  medium: "Trung bình",
  low: "Thấp",
};

export function CompensationTable({ rows }: { rows: CompensationItem[] }) {
  if (rows.length === 0) return null;

  return (
    <section className="section">
      <h2>Bù trừ bất thường (Lớp 2)</h2>
      <p className="muted section-desc">
        Cặp ngày thiếu / ngày bù — phát hiện tự động, không phải vi phạm Lớp 1 nếu khớp.
      </p>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Ngày thiếu</th>
              <th>Ngày bù</th>
              <th>Thiếu (h)</th>
              <th>Thừa (h)</th>
              <th>Độ tin</th>
              <th>Ghi chú</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={`${r.under_day}-${r.over_day}-${i}`} className="row-compensation">
                <td>{fmtDateVi(r.under_day)}</td>
                <td>{fmtDateVi(r.over_day)}</td>
                <td>{r.under_hours.toFixed(1)}</td>
                <td>{r.over_hours.toFixed(1)}</td>
                <td>
                  <span className={`badge badge-conf-${r.confidence}`}>
                    {CONF_LABEL[r.confidence] ?? r.confidence}
                  </span>
                </td>
                <td className="cell-message">{r.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
