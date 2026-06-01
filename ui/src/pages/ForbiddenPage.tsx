import { Link } from "react-router-dom";

export function ForbiddenPage({
  title = "Không có quyền truy cập",
  message = "Bạn cần đăng nhập với tài khoản có quyền phù hợp.",
}: {
  title?: string;
  message?: string;
}) {
  return (
    <div className="page">
      <div className="card-panel forbidden-panel">
        <h1>{title}</h1>
        <p className="muted">{message}</p>
        <Link to="/" className="btn-secondary btn-sm">
          Về trang chủ
        </Link>
      </div>
    </div>
  );
}
