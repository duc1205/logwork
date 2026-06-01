import {
  addDays,
  addMonths,
  canGoNextPeriod,
  currentMonth,
  fmtRangeVi,
  monthRange,
  type PeriodMode,
  type PeriodSelection,
  todayIso,
  weekRange,
  weekStart,
} from "../utils/period";

interface Props {
  value: PeriodSelection;
  onChange: (next: PeriodSelection) => void;
}

export function PeriodPicker({ value, onChange }: Props) {
  const today = todayIso();

  function setMode(mode: PeriodMode) {
    if (mode === value.mode) return;
    if (mode === "month") {
      onChange({ ...value, mode: "month", month: currentMonth() });
    } else {
      const { start, end } = weekRange(today);
      onChange({ ...value, mode: "week", start, end });
    }
  }

  function shiftWeek(delta: number) {
    const ns = addDays(value.start, delta * 7);
    const { start, end } = weekRange(ns);
    onChange({ ...value, mode: "week", start, end });
  }

  function shiftMonth(delta: number) {
    onChange({ ...value, mode: "month", month: addMonths(value.month, delta) });
  }

  function onWeekStartChange(start: string) {
    if (!start) return;
    const end = addDays(weekStart(start), 6);
    onChange({ ...value, mode: "week", start: weekStart(start), end });
  }

  const canNext = canGoNextPeriod(value);
  const monthBounds = value.mode === "month" ? monthRange(value.month) : null;

  return (
    <div className="period-picker">
      <div className="period-tabs">
        <button
          type="button"
          className={value.mode === "week" ? "active" : ""}
          onClick={() => setMode("week")}
        >
          Theo tuần
        </button>
        <button
          type="button"
          className={value.mode === "month" ? "active" : ""}
          onClick={() => setMode("month")}
        >
          Theo tháng
        </button>
      </div>

      {value.mode === "week" ? (
        <div className="period-fields">
          <div className="period-nav">
            <button type="button" className="btn-icon" title="Tuần trước" onClick={() => shiftWeek(-1)}>
              ◀
            </button>
            <button
              type="button"
              className="btn-icon"
              title="Tuần sau"
              disabled={!canNext}
              onClick={() => canNext && shiftWeek(1)}
            >
              ▶
            </button>
            <button
              type="button"
              className="btn-ghost btn-sm"
              onClick={() => {
                const { start, end } = weekRange(today);
                onChange({ ...value, mode: "week", start, end });
              }}
            >
              Tuần này
            </button>
          </div>
          <div className="period-dates">
            <label>
              Từ ngày
              <input
                type="date"
                value={value.start}
                max={value.end}
                onChange={(e) => onWeekStartChange(e.target.value)}
              />
            </label>
            <label>
              Đến ngày
              <input type="date" value={value.end} readOnly className="readonly" />
            </label>
          </div>
          <p className="period-range-label">
            Tuần: <strong>{fmtRangeVi(value.start, value.end)}</strong>
          </p>
        </div>
      ) : (
        <div className="period-fields">
          <div className="period-nav">
            <button type="button" className="btn-icon" title="Tháng trước" onClick={() => shiftMonth(-1)}>
              ◀
            </button>
            <button
              type="button"
              className="btn-icon"
              title="Tháng sau"
              disabled={!canNext}
              onClick={() => canNext && shiftMonth(1)}
            >
              ▶
            </button>
            <button
              type="button"
              className="btn-ghost btn-sm"
              onClick={() => onChange({ ...value, mode: "month", month: currentMonth() })}
            >
              Tháng này
            </button>
          </div>
          <div className="period-dates">
            <label className="period-month-label">
              Chọn tháng
              <input
                type="month"
                value={value.month}
                max={currentMonth()}
                onChange={(e) =>
                  e.target.value && onChange({ ...value, mode: "month", month: e.target.value })
                }
              />
            </label>
          </div>
          {monthBounds && (
            <p className="period-range-label">
              Tháng: <strong>{fmtRangeVi(monthBounds.start, monthBounds.end)}</strong>
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export function defaultPeriod(): PeriodSelection {
  const today = todayIso();
  const { start, end } = weekRange(today);
  return { mode: "week", start, end, month: currentMonth() };
}
