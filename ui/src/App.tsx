import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { useAuth } from "./context/AuthContext";
import { DashboardPage } from "./pages/DashboardPage";
import { GoldenComparePage } from "./pages/GoldenComparePage";
import { HeatmapPage } from "./pages/HeatmapPage";
import { LoginPage } from "./pages/LoginPage";
import { NotificationsPage } from "./pages/NotificationsPage";
import { ForbiddenPage } from "./pages/ForbiddenPage";
import { SettingsPage } from "./pages/SettingsPage";
import { isQaRole, isSettingsAdmin } from "./utils/roles";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page-loading full">Đang tải…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function QaRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page-loading full">Đang tải…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!isQaRole(user.role)) {
    return (
      <ForbiddenPage
        title="Cần quyền QA"
        message="Chỉ tài khoản trong LOGWORK_QA_USERS (quyền Logwork, không phải Administrator Jira)."
      />
    );
  }
  return <>{children}</>;
}

function SettingsAdminRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page-loading full">Đang tải…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!isSettingsAdmin(user.role)) {
    return (
      <ForbiddenPage
        title="Cần quyền cấu hình Logwork"
        message="Chỉ tài khoản trong LOGWORK_ADMIN_USERS mới chỉnh phạt, ngày lễ và OT. Không cần quyền Administrator trên Jira."
      />
    );
  }
  return <>{children}</>;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  return <QaRoute>{children}</QaRoute>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="heatmap" element={<HeatmapPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route
          path="admin/settings"
          element={
            <SettingsAdminRoute>
              <SettingsPage />
            </SettingsAdminRoute>
          }
        />
        <Route
          path="admin/golden"
          element={
            <AdminRoute>
              <GoldenComparePage />
            </AdminRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
