import { FormEvent, useState } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { user, loading, login } = useAuth();
  const [searchParams] = useSearchParams();
  const expired = searchParams.get("expired") === "1";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) {
    return <Navigate to="/" replace />;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(username.trim(), password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Đăng nhập thất bại");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <span className="brand-icon lg">⏱</span>
          <h1>Logwork QA Audit</h1>
          <p>Nhân viên xem tổng hợp cá nhân · QA đối soát team · Cấu hình hệ thống (theo danh sách env)</p>
        </div>

        {expired && (
          <div className="alert alert-warn">Phiên đăng nhập hết hạn — vui lòng đăng nhập lại.</div>
        )}

        <form onSubmit={onSubmit} className="login-form">
          <label>
            Username Jira
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="vd: ducnm1"
              autoComplete="username"
              required
            />
          </label>
          <label>
            Mật khẩu Jira
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>

          {error && <div className="alert alert-error">{error}</div>}

          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? "Đang kết nối Jira…" : "Đăng nhập & đối soát"}
          </button>
        </form>

        <footer className="login-hint">
          <p>
            Dùng cùng tài khoản{" "}
            <a href="https://jira.tinhvan.com" target="_blank" rel="noreferrer">
              jira.tinhvan.com
            </a>
            . Worklog lấy qua <strong>ProjectTimesheet</strong> — không cần quyền Administrator Jira.
          </p>
          <p className="muted login-role-hint">
            Quyền QA / cấu hình do server cấu hình (<code>LOGWORK_QA_USERS</code>,{" "}
            <code>LOGWORK_ADMIN_USERS</code>) — không đọc từ vai trò Jira.
          </p>
          <ul className="login-features">
            <li>Đối soát team theo tuần / tháng</li>
            <li>Phát hiện thiếu giờ, bù trừ, phạt MD</li>
            <li>So khớp golden file QA (admin)</li>
          </ul>
        </footer>
      </div>
    </div>
  );
}
