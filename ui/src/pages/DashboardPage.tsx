import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { api, ApiError } from "../api/client";
import type { PredictiveData, ScheduleInfo, WeeklySummary } from "../api/types";
import { CompensationTable } from "../components/CompensationTable";
import { DailyTable } from "../components/DailyTable";
import { ExportCsvButtons } from "../components/ExportCsvButtons";
import { PageHeader } from "../components/PageHeader";
import { PeriodPicker } from "../components/PeriodPicker";
import { PredictiveBanner } from "../components/PredictiveBanner";
import { ScheduleBanner } from "../components/ScheduleBanner";
import { StatCard } from "../components/StatCard";
import { TeamAuditTable } from "../components/TeamAuditTable";
import { useAuth } from "../context/AuthContext";
import { usePeriod } from "../context/PeriodContext";
import { isQaRole } from "../utils/roles";
import {
  fmtDateVi,
  fmtRangeVi,
  periodQueryString,
  todayIso,
} from "../utils/period";
import { sourceLabel, sourceTone } from "../utils/source";

export function DashboardPage() {
  const { user } = useAuth();
  const { period, setPeriod } = usePeriod();
  const [searchParams] = useSearchParams();
  const accountFromUrl = searchParams.get("account");
  const isQa = isQaRole(user?.role);
  const [team, setTeam] = useState<WeeklySummary[]>([]);
  const [summary, setSummary] = useState<WeeklySummary | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null);
  const [teamFilter, setTeamFilter] = useState("");
  const [schedule, setSchedule] = useState<ScheduleInfo | null>(null);
  const [predictive, setPredictive] = useState<PredictiveData | null>(null);
  const [metaLoading, setMetaLoading] = useState(true);
  const [teamLoading, setTeamLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [exporting, setExporting] = useState<"summary" | "compensation" | null>(null);
  const [error, setError] = useState("");

  const periodQuery = periodQueryString(period);
  const isMonth = period.mode === "month";
  const busy = metaLoading || teamLoading;

  useEffect(() => {
    let cancelled = false;
    setMetaLoading(true);
    setError("");

    const reqs: Promise<unknown>[] = [api.schedule(), api.predictive(periodQuery)];
    if (!isQa) {
      reqs.push(api.summary(periodQuery));
    }

    Promise.all(reqs)
      .then((results) => {
        if (cancelled) return;
        const sch = results[0] as ScheduleInfo;
        const pred = results[1] as PredictiveData;
        setSchedule(sch);
        setPredictive(pred);

        if (!isQa) {
          const selfSummary = results[2] as WeeklySummary;
          setSummary(selfSummary);
          setSelectedAccount(user?.account_id ?? null);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof ApiError ? e.message : String(e.message ?? e));
        }
      })
      .finally(() => {
        if (!cancelled) setMetaLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isQa, periodQuery, user?.account_id]);

  useEffect(() => {
    if (!isQa) return;
    let cancelled = false;
    setTeamLoading(true);
    setError("");

    api
      .allSummaries(periodQuery)
      .then((teamRows) => {
        if (cancelled) return;
        setTeam(teamRows);
        const fromUrl =
          accountFromUrl && teamRows.some((r) => r.account_id === accountFromUrl)
            ? accountFromUrl
            : null;
        const first =
          fromUrl ??
          teamRows.find((r) => r.missed_hours > 0)?.account_id ??
          teamRows[0]?.account_id ??
          null;
        setSelectedAccount(first);
        setSummary(null);
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof ApiError ? e.message : String(e.message ?? e));
        }
      })
      .finally(() => {
        if (!cancelled) setTeamLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isQa, periodQuery, accountFromUrl]);

  useEffect(() => {
    if (!isQa || !selectedAccount) return;
    let cancelled = false;
    setDetailLoading(true);
    api
      .summary(periodQuery, selectedAccount)
      .then((s) => {
        if (!cancelled) setSummary(s);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof ApiError ? e.message : String(e.message ?? e));
      })
      .finally(() => {
        if (!cancelled) setDetailLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isQa, selectedAccount, periodQuery]);

  const displaySummary = summary;
  const isPartialPeriod = displaySummary ? displaySummary.as_of < displaySummary.week_end : false;
  const isPastPeriod = displaySummary ? displaySummary.week_end < todayIso() : false;

  const stats = useMemo(() => {
    if (!displaySummary) return null;
    return {
      actualMd: (displaySummary.actual_hours / 8).toFixed(2),
      requiredMd: (displaySummary.required_hours / 8).toFixed(2),
      missedMd: (displaySummary.missed_hours / 8).toFixed(2),
    };
  }, [displaySummary]);

  const teamStats = useMemo(() => {
    if (!isQa || team.length === 0) return null;
    const withViolation = team.filter((r) => r.penalty > 0 || r.missed_hours > 0).length;
    const totalPenalty = team.reduce((s, r) => s + r.penalty, 0);
    return { count: team.length, withViolation, totalPenalty };
  }, [isQa, team]);

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

  if (metaLoading && !isQa && !displaySummary) {
    return <div className="page-loading">Đang tải worklog từ Jira…</div>;
  }

  return (
    <div className="page">
      <PageHeader
        title={isQa ? "Đối soát logwork QA" : isMonth ? "Tổng hợp tháng" : "Tổng hợp tuần"}
        subtitle={
          <>
            Dữ liệu trực tiếp từ <strong>jira.tinhvan.com</strong> — ProjectTimesheet plugin
          </>
        }
        aside={schedule ? <ScheduleBanner schedule={schedule} /> : undefined}
      >
        <PeriodPicker value={period} onChange={setPeriod} />
        {displaySummary?.data_source && (
          <span className={`source-badge tone-${sourceTone(displaySummary.data_source)}`}>
            Nguồn: {sourceLabel(displaySummary.data_source)}
          </span>
        )}
        {displaySummary && isPastPeriod && (
          <p className="muted as-of-hint">
            Kỳ {fmtRangeVi(displaySummary.week_start, displaySummary.week_end)}
          </p>
        )}
        {displaySummary && isPartialPeriod && !isPastPeriod && (
          <p className="muted as-of-hint">
            Hiển thị đến {fmtDateVi(displaySummary.as_of)} — ngày chưa tới không tính
          </p>
        )}
        <ExportCsvButtons
          exporting={exporting}
          disabled={busy}
          isQa={isQa}
          onExport={handleExport}
        />
      </PageHeader>

      {isQa && teamLoading && (
        <div className="alert alert-info jira-sync-banner">
          <strong>Đang lấy worklog toàn team từ Jira…</strong>
          <p className="muted">ProjectTimesheet có thể mất 1–2 phút. Trang vẫn dùng được trong lúc chờ.</p>
        </div>
      )}

      {metaLoading && <p className="muted loading-inline">Đang tải lịch nhắc / cảnh báo…</p>}
      {error && (
        <div className="alert alert-error">
          <strong>Không lấy được dữ liệu Jira</strong>
          <p>{error}</p>
          <p className="muted">Kiểm tra VPN, đăng nhập lại, hoặc quyền truy cập ProjectTimesheet.</p>
        </div>
      )}

      {predictive && (
        <PredictiveBanner
          items={predictive.items}
          hint={predictive.hint}
          admin={isQa}
        />
      )}

      {isQa && teamStats && (
        <div className="team-stats-banner">
          <StatCard label="NV có logwork" value={String(teamStats.count)} />
          <StatCard
            label="NV vi phạm"
            value={String(teamStats.withViolation)}
            tone={teamStats.withViolation > 0 ? "warn" : "ok"}
          />
          <StatCard
            label="Tổng penalty team"
            value={teamStats.totalPenalty.toLocaleString("vi-VN") + " ₫"}
            tone={teamStats.totalPenalty > 0 ? "danger" : "ok"}
          />
        </div>
      )}

      {isQa && team.length > 0 && (
        <TeamAuditTable
          rows={team}
          selectedId={selectedAccount}
          onSelect={setSelectedAccount}
          filter={teamFilter}
          onFilterChange={setTeamFilter}
        />
      )}

      {detailLoading && <p className="muted loading-inline">Đang tải chi tiết NV…</p>}

      {displaySummary && stats && (
        <>
          {isQa && selectedAccount && (
            <h2 className="detail-heading">
              Chi tiết: <code>{selectedAccount}</code> — {displaySummary.display_name}
            </h2>
          )}

          <div className={`stat-grid${detailLoading ? " loading-dim" : ""}`}>
            <StatCard label="Actual (MD)" value={stats.actualMd} sub={`${displaySummary.actual_hours.toFixed(1)} giờ`} tone="ok" />
            <StatCard label="Required (MD)" value={stats.requiredMd} sub={`Target ${displaySummary.target_md} MD`} />
            <StatCard
              label="Missed (MD)"
              value={stats.missedMd}
              sub={displaySummary.missed_hours > 0 ? `${displaySummary.missed_hours.toFixed(1)} giờ thiếu` : "Không thiếu"}
              tone={displaySummary.missed_hours > 0 ? "warn" : "ok"}
            />
            <StatCard
              label="Penalty"
              value={displaySummary.penalty.toLocaleString("vi-VN") + " ₫"}
              tone={displaySummary.penalty > 0 ? "danger" : "ok"}
            />
            {displaySummary.holiday_count > 0 && (
              <StatCard
                label="Ngày lễ trong kỳ"
                value={String(displaySummary.holiday_count)}
                tone="ok"
              />
            )}
          </div>

          {displaySummary.note && (
            <div className="note-box">
              <strong>Ghi chú đối soát:</strong> {displaySummary.note}
            </div>
          )}

          <CompensationTable rows={displaySummary.compensation_pairs ?? []} />

          <section className="section">
            <h2>Chi tiết theo ngày</h2>
            <DailyTable rows={displaySummary.daily_audits} />
          </section>
        </>
      )}

      {isQa && !teamLoading && team.length === 0 && !error && (
        <div className="empty-state">
          <span>ℹ</span>
          <p>Không có worklog trên Jira trong kỳ đã chọn.</p>
        </div>
      )}
    </div>
  );
}
