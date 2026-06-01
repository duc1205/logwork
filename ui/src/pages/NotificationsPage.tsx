import { useEffect, useMemo, useState } from "react";

import { api, ApiError } from "../api/client";
import type { NotificationList, ScheduleInfo } from "../api/types";
import { NotificationCard } from "../components/NotificationCard";
import { PageHeader } from "../components/PageHeader";
import { PeriodPicker } from "../components/PeriodPicker";
import { useAuth } from "../context/AuthContext";
import { usePeriod } from "../context/PeriodContext";
import { isQaRole } from "../utils/roles";
import { fmtNextRun } from "../utils/datetime";
import { fmtRangeVi, periodQueryString } from "../utils/period";
import { sourceLabel } from "../utils/source";

export function NotificationsPage() {
  const { user } = useAuth();
  const { period, setPeriod } = usePeriod();
  const isQa = isQaRole(user?.role);
  const [data, setData] = useState<NotificationList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [triggering, setTriggering] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState("");
  const [schedule, setSchedule] = useState<ScheduleInfo | null>(null);
  const [search, setSearch] = useState("");

  const periodQuery = periodQueryString(period);
  const isMonth = period.mode === "month";
  const initialLoad = loading && !data;

  useEffect(() => {
    api.schedule().then(setSchedule).catch(() => setSchedule(null));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");

    api
      .notifications(periodQuery)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof ApiError ? e.message : String(e.message ?? e));
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [periodQuery]);

  const filteredItems = useMemo(() => {
    if (!data) return [];
    const q = search.trim().toLowerCase();
    if (!q) return data.items;
    return data.items.filter(
      (item) =>
        item.employee_id.toLowerCase().includes(q) ||
        item.display_name.toLowerCase().includes(q) ||
        item.subject.toLowerCase().includes(q),
    );
  }, [data, search]);

  async function reloadFromJira(refresh: boolean) {
    setRefreshing(true);
    setError("");
    try {
      const d = await api.notifications(periodQuery, refresh);
      setData(d);
      if (refresh) {
        setTriggerMsg("Đã đồng bộ lại từ Jira.");
      }
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String((e as Error).message));
    } finally {
      setRefreshing(false);
    }
  }

  async function handleTrigger() {
    setTriggering(true);
    setTriggerMsg("");
    setError("");
    try {
      const res = await api.triggerReminders();
      if (res.skipped) {
        setTriggerMsg(
          "Job bỏ qua: chưa có Jira credentials trên server. Dùng nút này khi đã đăng nhập QA.",
        );
      } else {
        const sent = Number(res.emails_sent ?? 0);
        const failed = Number(res.emails_failed ?? 0);
        const skipped = Number(res.emails_skipped ?? 0);
        setTriggerMsg(
          `Đã chạy job — ${res.notifications_count ?? 0} thông báo · tuần ${res.week_start} → ${res.week_end}` +
            (sent > 0 || failed > 0 || skipped > 0
              ? ` · Email: ${sent} gửi OK${failed ? `, ${failed} lỗi` : ""}${skipped ? `, ${skipped} bỏ qua (thiếu email/SMTP)` : ""}`
              : res.email_mode === "disabled"
                ? " · Chưa cấu hình SMTP (LOGWORK_SMTP_HOST)"
                : ""),
        );
      }
      await reloadFromJira(true);
      const sch = await api.schedule();
      setSchedule(sch);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String((e as Error).message));
    } finally {
      setTriggering(false);
    }
  }

  async function handlePurge() {
    if (!window.confirm("Xóa mọi batch thông báo đã lưu (kể cả dữ liệu cũ)?")) return;
    setError("");
    try {
      const res = await api.purgeNotifications();
      setTriggerMsg(res.message);
      await reloadFromJira(true);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String((e as Error).message));
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Thông báo"
        subtitle={schedule?.schedule_hint ?? data?.schedule_hint ?? "Mỗi 17:00 thứ Tư hàng tuần"}
        aside={
          isQa ? (
            <div className="export-actions">
              <button
                type="button"
                className="btn-secondary btn-sm"
                onClick={() => reloadFromJira(true)}
                disabled={refreshing || loading}
              >
                {refreshing ? "Đang sync…" : "Sync Jira"}
              </button>
              <button
                type="button"
                className="btn-secondary btn-sm"
                onClick={handleTrigger}
                disabled={triggering}
              >
                {triggering ? "Đang chạy…" : "Chạy job nhắc"}
              </button>
              <button type="button" className="btn-ghost btn-sm" onClick={handlePurge}>
                Xóa cache cũ
              </button>
            </div>
          ) : undefined
        }
      >
        {schedule && (
          <p className="muted schedule-next">
            Lần chạy tiếp: <strong>{fmtNextRun(schedule.next_run_at)}</strong>
            {schedule.scheduler_enabled ? " · Auto bật" : schedule.scheduler_configured ? "" : " · Auto tắt"}
            {schedule.last_run_at && (
              <>
                {" "}
                · Lần trước: {fmtNextRun(schedule.last_run_at)}
                {schedule.last_run_ok === false ? " (lỗi)" : schedule.last_run_ok ? " (OK)" : ""}
              </>
            )}
          </p>
        )}
        {isQa && schedule && !schedule.credentials_configured && (
          <div className="alert alert-warn compact">
            Job tự động cần <code>JIRA_USERNAME</code> trên server. Trigger thủ công dùng session QA đang đăng nhập.
          </div>
        )}
        <PeriodPicker value={period} onChange={setPeriod} />
        {data?.data_source && (
          <span className="source-badge tone-ok">Nguồn: {sourceLabel(data.data_source)}</span>
        )}
      </PageHeader>

      {initialLoad && <div className="page-loading">Đang tải từ Jira…</div>}
      {loading && data && <p className="muted loading-inline">Đang cập nhật…</p>}
      {error && <div className="alert alert-error">{error}</div>}
      {triggerMsg && <div className="alert alert-info">{triggerMsg}</div>}

      {!initialLoad && data && (
        <>
          <p className="muted week-label">
            {isMonth ? "Tháng" : "Tuần"} {fmtRangeVi(data.week_start, data.week_end)}
            {data.generated_at
              ? ` · Batch ${new Date(data.generated_at).toLocaleString("vi-VN")}`
              : " · Tính trực tiếp từ Jira"}
            {" · "}
            {filteredItems.length}/{data.total} thông báo
          </p>

          {isQa && data.total > 0 && (
            <input
              type="search"
              className="team-search notif-search"
              placeholder="Lọc theo NV / nội dung…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          )}

          {data.total === 0 && (
            <div className="empty-state">
              <span>✓</span>
              <p>
                Không có thông báo vi phạm trong {isMonth ? "tháng" : "tuần"} này.
              </p>
            </div>
          )}

          {data.total > 0 && filteredItems.length === 0 && (
            <p className="muted empty-table">Không có thông báo khớp bộ lọc.</p>
          )}
        </>
      )}

      <div className={`notif-list${loading && data ? " loading-dim" : ""}`}>
        {filteredItems.map((item) => (
          <NotificationCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}
