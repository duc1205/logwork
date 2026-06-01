import type { NotificationItem } from "../api/types";

function fmtWorkDate(iso: string | null): string | null {
  if (!iso) return null;
  return new Date(iso + "T12:00:00").toLocaleDateString("vi-VN", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
  });
}

export function NotificationCard({ item }: { item: NotificationItem }) {
  const when = fmtWorkDate(item.work_date) ?? new Date(item.created_at).toLocaleString("vi-VN");

  return (
    <article className="notif-card">
      <header>
        <span className="notif-type">{item.discrepancy_type ?? "Nhắc nhở"}</span>
        <div className="notif-meta">
          {item.channel && <span className="notif-channel">{item.channel}</span>}
          <time dateTime={item.work_date ?? item.created_at}>{when}</time>
        </div>
      </header>
      <h3>{item.subject}</h3>
      <p className="muted notif-who">
        {item.display_name} · <code>{item.employee_id}</code>
      </p>
      {item.recipient_email && (
        <p className="muted notif-recipient">Gửi tới: {item.recipient_email}</p>
      )}
      <p className="notif-body">{item.body}</p>
    </article>
  );
}
