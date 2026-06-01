import { useMemo, useState } from "react";

import type { WeeklySummary } from "../api/types";

type SortKey = "name" | "missed" | "penalty";

interface Props {
  rows: WeeklySummary[];
  selectedId: string | null;
  onSelect: (accountId: string) => void;
  filter: string;
  onFilterChange: (v: string) => void;
}

export function TeamAuditTable({
  rows,
  selectedId,
  onSelect,
  filter,
  onFilterChange,
}: Props) {
  const [violationsOnly, setViolationsOnly] = useState(false);
  const [sortBy, setSortBy] = useState<SortKey>("missed");

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    let list = q
      ? rows.filter(
          (r) =>
            r.account_id.toLowerCase().includes(q) ||
            r.display_name.toLowerCase().includes(q),
        )
      : [...rows];

    if (violationsOnly) {
      list = list.filter((r) => r.missed_hours > 0 || r.penalty > 0);
    }

    list.sort((a, b) => {
      if (sortBy === "missed") return b.missed_hours - a.missed_hours;
      if (sortBy === "penalty") return b.penalty - a.penalty;
      return a.display_name.localeCompare(b.display_name, "vi");
    });

    return list;
  }, [rows, filter, violationsOnly, sortBy]);

  const withIssues = rows.filter((r) => r.missed_hours > 0 || r.penalty > 0);

  return (
    <section className="section team-audit">
      <div className="section-head team-head">
        <h2>Đối soát team ({filtered.length} NV)</h2>
        <div className="team-controls">
          <input
            type="search"
            className="team-search"
            placeholder="Tìm account / tên…"
            value={filter}
            onChange={(e) => onFilterChange(e.target.value)}
            aria-label="Tìm nhân viên"
          />
          <label className="team-toggle">
            <input
              type="checkbox"
              checked={violationsOnly}
              onChange={(e) => setViolationsOnly(e.target.checked)}
            />
            Chỉ vi phạm
          </label>
          <select
            className="team-sort"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortKey)}
            aria-label="Sắp xếp"
          >
            <option value="missed">Thiếu MD ↓</option>
            <option value="penalty">Penalty ↓</option>
            <option value="name">Tên A→Z</option>
          </select>
        </div>
      </div>
      <p className="muted section-desc">
        Dữ liệu worklog lấy trực tiếp từ Jira ProjectTimesheet. Chọn một dòng để xem chi tiết ngày.
        {withIssues.length > 0 && (
          <> · <strong>{withIssues.length}</strong> NV có thiếu / phạt</>
        )}
      </p>
      <div className="table-wrap">
        <table className="data-table team-table">
          <thead>
            <tr>
              <th>Account Jira</th>
              <th>Tên</th>
              <th>Actual MD</th>
              <th>Required MD</th>
              <th>Missed MD</th>
              <th>Penalty (₫)</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => {
              const missed = r.missed_hours / 8;
              const active = selectedId === r.account_id;
              return (
                <tr
                  key={r.account_id}
                  className={`team-row${active ? " selected" : ""}${missed > 0 ? " row-miss" : ""}`}
                  onClick={() => onSelect(r.account_id)}
                  role="button"
                  tabIndex={0}
                  aria-selected={active}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onSelect(r.account_id);
                    }
                  }}
                >
                  <td><code>{r.account_id}</code></td>
                  <td>{r.display_name}</td>
                  <td>{(r.actual_hours / 8).toFixed(2)}</td>
                  <td>{(r.required_hours / 8).toFixed(2)}</td>
                  <td className={missed > 0 ? "text-warn" : ""}>{missed.toFixed(2)}</td>
                  <td className={r.penalty > 0 ? "text-danger" : ""}>
                    {r.penalty > 0 ? r.penalty.toLocaleString("vi-VN") : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <p className="muted empty-table">Không có NV khớp bộ lọc / chưa có logwork trên Jira.</p>
        )}
      </div>
    </section>
  );
}
