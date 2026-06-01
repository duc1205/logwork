import type { PredictiveAlert } from "../api/types";

interface Props {
  items: PredictiveAlert[];
  hint?: string;
  admin?: boolean;
}

export function PredictiveBanner({ items, hint, admin }: Props) {
  if (items.length === 0 && !hint) return null;

  return (
    <div className={`predictive-banner${items.length === 0 && hint ? " hint-only" : ""}`}>
      <div className="predictive-header">
        <span className="predictive-icon">⚡</span>
        <strong>Cảnh báo sớm (predictive)</strong>
        {admin && items.length > 0 && (
          <span className="badge badge-amber">{items.length} NV</span>
        )}
      </div>
      {hint && items.length === 0 && <p className="predictive-hint-only">{hint}</p>}
      {items.length > 0 && (
        <ul className="predictive-list">
          {items.map((a) => (
            <li key={`${a.employee_id}-${a.alert_type}`}>
              {admin && (
                <span className="predictive-who">
                  {a.display_name} (@{a.employee_id})
                </span>
              )}
              <span className={`badge badge-type-${a.alert_type}`}>
                {a.alert_type === "midweek_pace" ? "Pace tuần" : "Pattern"}
              </span>
              <p>{a.message}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
