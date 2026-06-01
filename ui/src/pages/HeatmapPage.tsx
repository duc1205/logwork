import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api, ApiError } from "../api/client";
import type { HeatmapData } from "../api/types";
import { HeatmapGrid } from "../components/HeatmapGrid";
import { PeriodPicker } from "../components/PeriodPicker";
import { useAuth } from "../context/AuthContext";
import { usePeriod } from "../context/PeriodContext";
import { isQaRole } from "../utils/roles";
import {
  fmtDateVi,
  fmtRangeVi,
  periodQueryString,
} from "../utils/period";
import { sourceLabel, sourceTone } from "../utils/source";

export function HeatmapPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { period, setPeriod } = usePeriod();
  const isQa = isQaRole(user?.role);
  const [data, setData] = useState<HeatmapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState<"summary" | "compensation" | null>(null);
  const [error, setError] = useState("");

  const periodQuery = periodQueryString(period);
  const isMonth = period.mode === "month";

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");

    api
      .heatmap(periodQuery)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof ApiError ? e.message : String(e.message ?? e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [periodQuery]);

  async function handleExport(kind: "summary" | "compensation") {
    setExporting(kind);
    setError("");
    try {
      await api.downloadExport(kind, periodQuery);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e instanceof Error ? e.message : e));
    } finally {
      setExporting(null);
    }
  }

  function handleCellClick(employeeId: string) {
    if (!isQa) return;
    navigate(`/?account=${encodeURIComponent(employeeId)}`);
  }

  const isPartial = data ? data.as_of < data.week_end : false;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Heatmap logwork</h1>
          <p className="muted">
            {isQa
              ? "Toàn team — màu theo mức độ đối soát từng ngày"
              : "Trực quan hóa logwork cá nhân theo ngày"}
          </p>
          <PeriodPicker value={period} onChange={setPeriod} />
          {data?.data_source && (
            <span className={`source-badge tone-${sourceTone(data.data_source)}`}>
              Nguồn: {sourceLabel(data.data_source)}
            </span>
          )}
          {data && (
            <p className="muted as-of-hint">
              {isMonth ? "Tháng" : "Tuần"} {fmtRangeVi(data.week_start, data.week_end)}
              {isPartial && ` · Hiển thị đến ${fmtDateVi(data.as_of)}`}
            </p>
          )}
          <div className="export-actions">
            <button
              type="button"
              className="btn-secondary btn-sm"
              disabled={!!exporting || loading}
              onClick={() => handleExport("summary")}
            >
              {exporting === "summary" ? "Đang tải…" : isQa ? "Export CSV team" : "Export CSV của tôi"}
            </button>
            <button
              type="button"
              className="btn-secondary btn-sm"
              disabled={!!exporting || loading}
              onClick={() => handleExport("compensation")}
            >
              {exporting === "compensation" ? "Đang tải…" : isQa ? "Export bù trừ team" : "Export bù trừ"}
            </button>
          </div>
        </div>
      </header>

      {loading && isQa && !data && (
        <div className="alert alert-info jira-sync-banner">
          <strong>Đang tải heatmap team từ Jira…</strong>
          <p className="muted">Có thể mất vài phút với nhiều nhân viên.</p>
        </div>
      )}

      {loading && !data && !isQa && <div className="page-loading">Đang tải heatmap…</div>}
      {error && <div className="alert alert-error">{error}</div>}
      {loading && data && <p className="muted loading-inline">Đang cập nhật…</p>}

      {data && (
        <section className={`section${loading ? " loading-dim" : ""}`}>
          <HeatmapGrid
            cells={data.cells}
            onCellClick={isQa ? handleCellClick : undefined}
          />
        </section>
      )}
    </div>
  );
}
