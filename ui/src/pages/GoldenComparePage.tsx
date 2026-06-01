import { useState } from "react";

import { api, ApiError } from "../api/client";
import type { GoldenCompareResult } from "../api/types";
import { PageHeader } from "../components/PageHeader";
import { PeriodPicker } from "../components/PeriodPicker";
import { usePeriod } from "../context/PeriodContext";
import { fmtRangeVi, periodQueryString } from "../utils/period";

export function GoldenComparePage() {
  const { period, setPeriod } = usePeriod();
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<GoldenCompareResult | null>(null);
  const [validateResult, setValidateResult] = useState<{
    rows: number;
    errors: string[];
    warnings: string[];
    ok: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [exporting, setExporting] = useState<"summary" | "compensation" | null>(null);
  const [error, setError] = useState("");

  const periodQuery = periodQueryString(period);

  async function handleCompare(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Chọn file CSV golden QA");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    setValidateResult(null);
    try {
      const r = await api.goldenCompare(file, periodQuery);
      setResult(r);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleValidate() {
    if (!file) {
      setError("Chọn file CSV golden QA");
      return;
    }
    setValidating(true);
    setError("");
    setValidateResult(null);
    try {
      const r = await api.goldenValidate(file);
      setValidateResult(r);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setValidating(false);
    }
  }

  async function handleExport(kind: "summary" | "compensation") {
    setExporting(kind);
    setError("");
    try {
      await api.downloadExport(kind, periodQuery);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setExporting(null);
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Golden QA Compare"
        subtitle="Admin: upload CSV golden QA, so khớp với kết quả engine cùng kỳ (tuần/tháng)."
      />

      <form className="golden-form section" onSubmit={handleCompare}>
        <PeriodPicker value={period} onChange={setPeriod} />
        <label className="file-label">
          File golden CSV
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>
        <button type="submit" className="btn-primary" disabled={loading || !file}>
          {loading ? "Đang so khớp…" : "So khớp với engine"}
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={validating || !file}
          onClick={handleValidate}
        >
          {validating ? "Đang kiểm tra…" : "Validate CSV (không cần Jira)"}
        </button>
        <div className="export-actions">
          <button
            type="button"
            className="btn-secondary btn-sm"
            disabled={!!exporting}
            onClick={() => handleExport("summary")}
          >
            {exporting === "summary" ? "Đang tải…" : "Tải engine CSV summary"}
          </button>
          <button
            type="button"
            className="btn-secondary btn-sm"
            disabled={!!exporting}
            onClick={() => handleExport("compensation")}
          >
            {exporting === "compensation" ? "Đang tải…" : "Tải engine CSV bù trừ"}
          </button>
        </div>
      </form>

      {validateResult && (
        <div className={`golden-result section ${validateResult.ok ? "ok" : "fail"}`}>
          <h2>{validateResult.ok ? "✓ CSV hợp lệ" : "✗ CSV có lỗi"}</h2>
          <p className="muted">{validateResult.rows} dòng</p>
          {validateResult.errors.length > 0 && (
            <ul>
              {validateResult.errors.map((e) => (
                <li key={e}>{e}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="section">
          <div className={`golden-result ${result.ok ? "ok" : "fail"}`}>
            <h2>{result.ok ? "✓ Khớp golden" : "✗ Lệch golden"}</h2>
            <p className="muted">
              Kỳ {fmtRangeVi(result.week_start, result.week_end)} · Engine {result.engine_rows} dòng ·
              Golden {result.golden_rows} dòng · Khớp {result.matched}
            </p>
          </div>

          {result.errors.length > 0 && (
            <div className="alert alert-error">
              <strong>Lỗi ({result.errors.length})</strong>
              <ul>
                {result.errors.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            </div>
          )}

          {result.warnings.length > 0 && (
            <div className="alert alert-warn">
              <strong>Cảnh báo ({result.warnings.length})</strong>
              <ul>
                {result.warnings.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Account</th>
                  <th>Engine Missed MD</th>
                  <th>Golden Missed MD</th>
                  <th>Engine Penalty</th>
                  <th>Golden Penalty</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {result.rows.map((r) => (
                  <tr key={r.account} className={`row-golden-${r.status}`}>
                    <td>{r.account}</td>
                    <td>{r.engine_missed_md?.toFixed(2) ?? "—"}</td>
                    <td>{r.golden_missed_md?.toFixed(2) ?? "—"}</td>
                    <td>{r.engine_penalty?.toLocaleString("vi-VN") ?? "—"}</td>
                    <td>{r.golden_penalty?.toLocaleString("vi-VN") ?? "—"}</td>
                    <td>
                      <span className={`badge badge-golden-${r.status}`}>{r.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
