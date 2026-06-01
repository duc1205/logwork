# Chạy Logwork trên máy local

## 1. Yêu cầu

| Thành phần | Phiên bản gợi ý |
|------------|------------------|
| Python | 3.11+ |
| Node.js | 18+ |
| Git | clone repo GitLab |

## 2. Clone và cấu trúc thư mục

Package Python tên **`logwork`**, nên đặt repo tại **`d:\logwork`** và chạy lệnh từ **`d:\`**:

```powershell
git clone https://gitlabtv.tinhvan.com/tvs-tinhvan-solution/tvs/tvh-ai/jira-report.git d:\logwork
cd d:\
```

Nếu clone vào tên khác (vd. `jira-report`), đổi tên thư mục thành `logwork` hoặc thêm `d:\` vào `PYTHONPATH` và dùng đúng tên package.

## 3. Cài dependency

```powershell
cd d:\
pip install -r logwork\requirements-api.txt

cd d:\logwork\ui
npm install
```

## 4. Chạy dev (khuyên dùng)

Một lệnh mở 2 cửa sổ (API + UI):

```powershell
cd d:\
.\logwork\scripts\run_dev.ps1
```

| Dịch vụ | URL |
|---------|-----|
| UI | http://localhost:5173 |
| API health | http://127.0.0.1:8001/api/health |

UI gọi API qua **Vite proxy** (`/api` → `127.0.0.1:8001`). File `ui/.env` có `LOGWORK_API_PROXY=http://127.0.0.1:8001`.

### Chạy thủ công (2 terminal)

**Terminal 1 — API:**

```powershell
cd d:\
$env:LOGWORK_DATA_DIR="d:\logwork\fixtures\live"
$env:LOGWORK_DISABLE_SCHEDULER="1"
python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 2 — UI:**

```powershell
cd d:\logwork\ui
npm run dev
```

## 5. Dữ liệu & biến môi trường

| Biến | Mặc định / gợi ý |
|------|-------------------|
| `LOGWORK_DATA_DIR` | `d:\logwork\fixtures\live` (phải có `config.json`) |
| `LOGWORK_DISABLE_SCHEDULER` | `1` khi dev (không chạy job 17h T4) |
| `LOGWORK_QA_USERS` | Danh sách user QA (server) |
| `LOGWORK_ADMIN_USERS` | User được trang Cấu hình |

Nếu dashboard **Internal Server Error**: mở http://127.0.0.1:8001/api/health — `data_dir` phải trỏ tới thư mục có `config.json`. Xóa biến `LOGWORK_DATA_DIR` cũ trong Windows nếu trỏ path không tồn tại.

## 6. Đăng nhập UI

- **Username / mật khẩu:** tài khoản https://jira.tinhvan.com
- Không cần quyền Jira Administrator
- QA/Admin: cấu hình trên server qua env (không lấy từ role Jira)

## 7. Chia sẻ LAN (cùng WiFi/VPN)

```powershell
cd d:\
.\logwork\scripts\run_lan.ps1
```

Script bật API `0.0.0.0:8001`, UI `0.0.0.0:5173`, `LOGWORK_ALLOW_LAN=1`. Đồng nghiệp mở `http://<IP-LAN>:5173/`.

## 8. Kiểm tra kết nối UI ↔ API

- Sidebar / login: dòng **BE:** — dev hiển thị proxy `127.0.0.1:8001`
- Health OK: **● Jira live** + đường dẫn `fixtures/live`

## 9. Build UI (tùy chọn)

```powershell
cd d:\logwork\ui
npm run build
npm run preview
```

Preview vẫn proxy `/api` về `8001` — cần API đang chạy.

## 10. CLI không qua UI

```powershell
cd d:\
python -m logwork test
python -m logwork reconcile --month 2026-05
```
