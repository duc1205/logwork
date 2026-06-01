import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { apiEndpointLabel } from "../api/base";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { isQaRole, isSettingsAdmin, roleLabel } from "../utils/roles";

export function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [liveOk, setLiveOk] = useState<boolean | null>(null);
  const [dataDir, setDataDir] = useState<string | null>(null);
  const [navOpen, setNavOpen] = useState(false);

  useEffect(() => {
    api
      .health()
      .then((h) => {
        setLiveOk(h.status === "ok" && h.mode === "jira_live");
        setDataDir(h.data_dir ?? null);
      })
      .catch(() => {
        setLiveOk(false);
        setDataDir(null);
      });
  }, []);

  useEffect(() => {
    setNavOpen(false);
  }, [location.pathname]);

  return (
    <div className="app-shell">
      {navOpen && (
        <button
          type="button"
          className="nav-overlay"
          aria-label="Đóng menu"
          onClick={() => setNavOpen(false)}
        />
      )}

      <header className="mobile-header">
        <button
          type="button"
          className="nav-toggle"
          aria-label="Mở menu"
          aria-expanded={navOpen}
          onClick={() => setNavOpen((v) => !v)}
        >
          ☰
        </button>
        <strong>Logwork QA</strong>
        <span className={`role-badge role-${user?.role ?? "employee"}`}>
          {roleLabel(user?.role)}
        </span>
      </header>

      <aside className={`sidebar${navOpen ? " open" : ""}`}>
        <div className="brand">
          <span className="brand-icon">⏱</span>
          <div>
            <strong>Logwork QA</strong>
            <small>Đối soát Jira</small>
          </div>
        </div>

        <nav className="nav" aria-label="Chính">
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            {isQaRole(user?.role) ? "Đối soát QA" : "Tổng hợp"}
          </NavLink>
          <NavLink to="/heatmap" className={({ isActive }) => (isActive ? "active" : "")}>
            Heatmap
          </NavLink>
          <NavLink to="/notifications" className={({ isActive }) => (isActive ? "active" : "")}>
            Thông báo
          </NavLink>
          {isSettingsAdmin(user?.role) && (
            <NavLink to="/admin/settings" className={({ isActive }) => (isActive ? "active" : "")}>
              Cấu hình
            </NavLink>
          )}
          {isQaRole(user?.role) && (
            <NavLink to="/admin/golden" className={({ isActive }) => (isActive ? "active" : "")}>
              Golden QA
            </NavLink>
          )}
        </nav>

        <div className="sidebar-footer">
          <p className="sidebar-api-endpoint muted" title="Đích API mà UI đang gọi">
            BE: <code>{apiEndpointLabel()}</code>
          </p>
          {liveOk !== null && (
            <p className={`sidebar-status${liveOk ? " ok" : " err"}`}>
              {liveOk ? "● Jira live" : "● API offline"}
              {dataDir && liveOk && (
                <small className="sidebar-data-dir" title={dataDir}>
                  {" "}
                  · {dataDir.replace(/^.*[\\/]/, "")}
                </small>
              )}
            </p>
          )}
          <div className="user-chip">
            <span className="avatar">{user?.display_name?.charAt(0) ?? "?"}</span>
            <div>
              <strong>{user?.display_name}</strong>
              <small>
                @{user?.account_id}
                <span className={`role-badge role-${user?.role ?? "employee"}`}>
                  {roleLabel(user?.role)}
                </span>
              </small>
            </div>
          </div>
          <button type="button" className="btn-ghost" onClick={logout}>
            Đăng xuất
          </button>
        </div>
      </aside>

      <main className="main" id="main">
        <Outlet />
      </main>
    </div>
  );
}
