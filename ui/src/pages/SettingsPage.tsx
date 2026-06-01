import { useEffect, useState } from "react";

import { AccountSearchPicker } from "../components/AccountSearchPicker";
import { api, ApiError } from "../api/client";
import type { AuditSettings, HolidayItem, OtRules, OvertimeItem } from "../api/types";

function fmtVnd(n: number) {
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(n);
}

function fmtDateVi(iso: string) {
  return new Date(iso + "T12:00:00").toLocaleDateString("vi-VN", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function SettingsPage() {
  const [settings, setSettings] = useState<AuditSettings | null>(null);
  const [holidays, setHolidays] = useState<HolidayItem[]>([]);
  const [otRules, setOtRules] = useState<OtRules | null>(null);
  const [overtime, setOvertime] = useState<OvertimeItem[]>([]);
  const [penalty, setPenalty] = useState("");
  const [tolerance, setTolerance] = useState("");
  const [compThreshold, setCompThreshold] = useState("");
  const [newDate, setNewDate] = useState("");
  const [newName, setNewName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [adding, setAdding] = useState(false);
  const [savingOt, setSavingOt] = useState(false);
  const [addingOt, setAddingOt] = useState(false);
  const [otAccount, setOtAccount] = useState("");
  const [otDate, setOtDate] = useState("");
  const [otHours, setOtHours] = useState("2");
  const [otReason, setOtReason] = useState("");
  const [otStatus, setOtStatus] = useState<"approved" | "pending">("approved");
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  async function loadAll() {
    setLoading(true);
    setError("");
    try {
      const [cfg, hol, otList] = await Promise.all([
        api.auditSettings(),
        api.holidays(),
        api.overtime(),
      ]);
      setSettings(cfg);
      setHolidays(hol.items);
      setOtRules(cfg.ot_rules);
      setOvertime(otList.items);
      setPenalty(String(cfg.penalty_per_md));
      setTolerance(String(cfg.tolerance_hours));
      setCompThreshold(String(cfg.compensation_threshold));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleSavePenalty(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMsg("");
    setError("");
    try {
      const body: {
        penalty_per_md?: number;
        tolerance_hours?: number;
        compensation_threshold?: number;
      } = {};
      const p = Number(penalty.replace(/\D/g, ""));
      if (!Number.isFinite(p) || p < 0) {
        throw new Error("Mức phạt không hợp lệ");
      }
      body.penalty_per_md = Math.round(p);
      const tol = Number(tolerance);
      if (Number.isFinite(tol) && tol >= 0) body.tolerance_hours = tol;
      const ct = Number(compThreshold);
      if (Number.isFinite(ct) && ct > 0) body.compensation_threshold = ct;

      const cfg = await api.updateAuditSettings(body);
      setSettings(cfg);
      setMsg(`Đã lưu — phạt ${fmtVnd(cfg.penalty_per_md)}/MD`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveOtRules(e: React.FormEvent) {
    e.preventDefault();
    if (!otRules) return;
    setSavingOt(true);
    setMsg("");
    setError("");
    try {
      const updated = await api.updateOtRules(otRules);
      setOtRules(updated);
      setMsg("Đã lưu quy tắc làm ngoài giờ");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setSavingOt(false);
    }
  }

  async function handleAddOvertime(e: React.FormEvent) {
    e.preventDefault();
    if (!otAccount.trim() || !otDate) return;
    setAddingOt(true);
    setMsg("");
    setError("");
    try {
      const account = otAccount.trim().toLowerCase();
      const date = otDate;
      const res = await api.addOvertime({
        employee_id: account,
        ot_date: date,
        ot_hours: Number(otHours),
        reason: otReason.trim(),
        status: otStatus,
      });
      setOvertime(res.items);
      setOtAccount("");
      setOtDate("");
      setOtHours("2");
      setOtReason("");
      setMsg(`Đã thêm OT @${account} ngày ${date} (${otStatus})`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setAddingOt(false);
    }
  }

  async function handleDeleteOt(employeeId: string, otDate: string) {
    if (!window.confirm(`Xóa OT ${employeeId} ngày ${otDate}?`)) return;
    try {
      const res = await api.deleteOvertime(employeeId, otDate);
      setOvertime(res.items);
      setMsg(`Đã xóa OT ${employeeId} ${otDate}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    }
  }

  function patchOtRules(patch: Partial<OtRules>) {
    setOtRules((prev) => (prev ? { ...prev, ...patch } : prev));
  }

  async function handleAddHoliday(e: React.FormEvent) {
    e.preventDefault();
    if (!newDate || !newName.trim()) return;
    setAdding(true);
    setMsg("");
    setError("");
    try {
      const res = await api.addHoliday({
        holiday_date: newDate,
        name: newName.trim(),
        is_company_wide: true,
      });
      setHolidays(res.items);
      setNewDate("");
      setNewName("");
      setMsg(`Đã thêm ngày nghỉ ${newDate}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setAdding(false);
    }
  }

  async function handleDelete(date: string) {
    if (!window.confirm(`Xóa ngày nghỉ ${date}?`)) return;
    setError("");
    try {
      const res = await api.deleteHoliday(date);
      setHolidays(res.items);
      setMsg(`Đã xóa ngày ${date}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    }
  }

  if (loading) {
    return <div className="page-loading">Đang tải cấu hình…</div>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Cấu hình đối soát</h1>
          <p className="muted">
            Chỉ tài khoản trong <code>LOGWORK_ADMIN_USERS</code> (quyền cấu hình Logwork —{" "}
            <strong>không</strong> phải Administrator Jira). Đăng nhập bằng username/password Jira bình thường.
            Mức phạt, ngày nghỉ lễ và quy tắc OT áp dụng cho mọi lần đối soát.
            {settings?.data_dir && <> · <code>{settings.data_dir}</code></>}
          </p>
        </div>
      </header>

      {error && <div className="alert alert-error">{error}</div>}
      {msg && <div className="alert alert-info">{msg}</div>}

      <section className="settings-section card-panel">
        <h2>Mức tiền phạt</h2>
        <p className="muted">
          Công thức: <strong>Phạt = MD thiếu × penalty_per_md</strong> (1 MD = 8 giờ).
          Hiện tại: {settings ? fmtVnd(settings.penalty_per_md) : "—"}/MD.
        </p>
        <form className="settings-form" onSubmit={handleSavePenalty}>
          <label>
            Phạt mỗi MD thiếu (VNĐ)
            <input
              type="text"
              inputMode="numeric"
              value={penalty}
              onChange={(e) => setPenalty(e.target.value)}
              placeholder="20000"
            />
          </label>
          <label>
            Sai số giờ (tolerance)
            <input
              type="number"
              step="0.05"
              min="0"
              value={tolerance}
              onChange={(e) => setTolerance(e.target.value)}
            />
          </label>
          <label>
            Ngưỡng bù trừ Lớp 2 (giờ)
            <input
              type="number"
              step="0.5"
              min="0.5"
              value={compThreshold}
              onChange={(e) => setCompThreshold(e.target.value)}
            />
          </label>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? "Đang lưu…" : "Lưu cấu hình phạt"}
          </button>
        </form>
      </section>

      <section className="settings-section card-panel">
        <h2>Ngày nghỉ lễ</h2>
        <p className="muted">NV không bắt buộc logwork; log trên ngày lễ sẽ bị cảnh báo.</p>

        <form className="settings-form settings-form-inline" onSubmit={handleAddHoliday}>
          <label>
            Ngày
            <input type="date" value={newDate} onChange={(e) => setNewDate(e.target.value)} required />
          </label>
          <label className="grow">
            Tên
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Quốc tế Lao động"
              required
            />
          </label>
          <button type="submit" className="btn-secondary" disabled={adding}>
            {adding ? "Đang thêm…" : "Thêm ngày lễ"}
          </button>
        </form>

        {holidays.length === 0 ? (
          <p className="muted empty-inline">Chưa có ngày nghỉ lễ.</p>
        ) : (
          <table className="data-table settings-table">
            <thead>
              <tr>
                <th>Ngày</th>
                <th>Tên</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {holidays.map((h) => (
                <tr key={h.holiday_date}>
                  <td>{fmtDateVi(h.holiday_date)}</td>
                  <td>{h.name}</td>
                  <td>
                    <button
                      type="button"
                      className="btn-ghost btn-sm"
                      onClick={() => handleDelete(h.holiday_date)}
                    >
                      Xóa
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {otRules && (
        <section className="settings-section card-panel">
          <h2>Quy tắc làm ngoài giờ (OT)</h2>
          <p className="muted">
            ValidMax = min(8h + min(OT duyệt, max OT/ngày) + grace, trần ngày). Log vượt ValidMax →{" "}
            <code>over_hours</code>.
          </p>
          <form className="settings-form settings-form-wide" onSubmit={handleSaveOtRules}>
            <label>
              OT tối đa / ngày (giờ)
              <input
                type="number"
                step="0.5"
                min="0"
                value={otRules.max_ot_hours_per_day}
                onChange={(e) => patchOtRules({ max_ot_hours_per_day: Number(e.target.value) })}
              />
            </label>
            <label>
              Trần log tối đa / ngày (giờ)
              <input
                type="number"
                step="0.5"
                min="1"
                value={otRules.max_daily_hours}
                onChange={(e) => patchOtRules({ max_daily_hours: Number(e.target.value) })}
              />
            </label>
            <label>
              Grace không cần OT (giờ)
              <input
                type="number"
                step="0.25"
                min="0"
                value={otRules.ot_grace_hours}
                onChange={(e) => patchOtRules({ ot_grace_hours: Number(e.target.value) })}
              />
            </label>
            <div className="settings-checks">
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={otRules.accept_approved}
                  onChange={(e) => patchOtRules({ accept_approved: e.target.checked })}
                />
                Chấp nhận OT đã duyệt (approved)
              </label>
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={otRules.accept_pending}
                  onChange={(e) => patchOtRules({ accept_pending: e.target.checked })}
                />
                Chấp nhận OT chờ duyệt (pending)
              </label>
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={otRules.allow_weekend_logging}
                  onChange={(e) => patchOtRules({ allow_weekend_logging: e.target.checked })}
                />
                Cho phép log cuối tuần (không cảnh báo)
              </label>
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={otRules.allow_holiday_logging}
                  onChange={(e) => patchOtRules({ allow_holiday_logging: e.target.checked })}
                />
                Cho phép log ngày lễ
              </label>
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={otRules.allow_leave_logging}
                  onChange={(e) => patchOtRules({ allow_leave_logging: e.target.checked })}
                />
                Cho phép log ngày nghỉ phép
              </label>
            </div>
            <button type="submit" className="btn-primary" disabled={savingOt}>
              {savingOt ? "Đang lưu…" : "Lưu quy tắc OT"}
            </button>
          </form>
        </section>
      )}

      <section className="settings-section card-panel">
        <h2>OT đã đăng ký (duyệt thủ công)</h2>
        <p className="muted">
          Jira live chưa có API OT — QA thêm bản ghi approved tại đây để nới ValidMax cho NV.
        </p>
        <form className="settings-form settings-form-inline settings-form-ot" onSubmit={handleAddOvertime}>
          <label className="account-picker-label">
            Account Jira
            <AccountSearchPicker
              value={otAccount}
              onChange={setOtAccount}
              placeholder="Tìm account / tên…"
              required
            />
          </label>
          <label>
            Ngày
            <input type="date" value={otDate} onChange={(e) => setOtDate(e.target.value)} required />
          </label>
          <label>
            Giờ OT
            <input
              type="number"
              step="0.5"
              min="0.5"
              value={otHours}
              onChange={(e) => setOtHours(e.target.value)}
              required
            />
          </label>
          <label>
            Trạng thái
            <select value={otStatus} onChange={(e) => setOtStatus(e.target.value as "approved" | "pending")}>
              <option value="approved">Đã duyệt</option>
              <option value="pending">Chờ duyệt</option>
            </select>
          </label>
          <label className="grow">
            Lý do
            <input
              type="text"
              value={otReason}
              onChange={(e) => setOtReason(e.target.value)}
              placeholder="Release hotfix"
            />
          </label>
          <button type="submit" className="btn-secondary" disabled={addingOt}>
            {addingOt ? "Đang thêm…" : "Thêm OT"}
          </button>
        </form>
        {overtime.length === 0 ? (
          <p className="muted empty-inline">Chưa có OT đăng ký.</p>
        ) : (
          <table className="data-table settings-table">
            <thead>
              <tr>
                <th>Account</th>
                <th>Tên</th>
                <th>Ngày</th>
                <th>Giờ</th>
                <th>Trạng thái</th>
                <th>Lý do</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {overtime.map((o) => (
                <tr key={`${o.employee_id}-${o.ot_date}`}>
                  <td><code>{o.employee_id}</code></td>
                  <td>{o.display_name ?? "—"}</td>
                  <td>{fmtDateVi(o.ot_date)}</td>
                  <td>{o.ot_hours}h</td>
                  <td>{o.status}</td>
                  <td>{o.reason || "—"}</td>
                  <td>
                    <button
                      type="button"
                      className="btn-ghost btn-sm"
                      onClick={() => handleDeleteOt(o.employee_id, o.ot_date)}
                    >
                      Xóa
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
