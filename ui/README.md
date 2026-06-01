# Logwork UI (React)

Giao diện web — gọi API `logwork/api/`. Hướng dẫn đầy đủ: [../docs/CHAY_LOCAL.md](../docs/CHAY_LOCAL.md)

## Chạy dev (localhost)

**Cách nhanh** (từ `d:\`):

```powershell
.\logwork\scripts\run_dev.ps1
```

**Hoặc 2 terminal:**

```powershell
# API (từ d:\)
$env:LOGWORK_DATA_DIR="d:\logwork\fixtures\live"
$env:LOGWORK_DISABLE_SCHEDULER="1"
python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port 8001 --reload

# UI
cd d:\logwork\ui
npm install
npm run dev
```

Mở http://localhost:5173

### UI → Backend

| Môi trường | Cách gọi API |
|------------|----------------|
| **`npm run dev`** | `fetch("/api/...")` → Vite proxy → `http://127.0.0.1:8001` |
| **`npm run preview`** | Cùng proxy trong `vite.config.ts` — API phải chạy :8001 |

Đổi port API:

```powershell
$env:LOGWORK_API_PROXY="http://127.0.0.1:8001"
npm run dev
```

Trên sidebar / login: **BE:** = endpoint đang dùng.

## Chia sẻ LAN

```powershell
cd d:\
.\logwork\scripts\run_lan.ps1
```

| Port | Dịch vụ |
|------|---------|
| 5173 | UI (`npm run dev:lan`) |
| 8001 | API (`LOGWORK_ALLOW_LAN=1`) |

Đồng nghiệp chỉ cần mở `http://<IP-server>:5173/`.

## Đăng nhập

Username + mật khẩu [jira.tinhvan.com](https://jira.tinhvan.com) — dữ liệu live qua ProjectTimesheet.

## Tính năng

- Tổng hợp tuần/tháng, bù trừ Lớp 2, heatmap, predictive
- Golden QA, cấu hình OT/phạt MD (admin)
- Export CSV, thông báo / job nhắc 17h T4

### Env server (tùy chọn)

| Biến | Mô tả |
|------|--------|
| `LOGWORK_QA_USERS` | Tài khoản QA |
| `LOGWORK_ADMIN_USERS` | Tài khoản cấu hình hệ thống |
| `LOGWORK_PROJECT_KEYS` | Lọc project Jira |
| `JIRA_USERNAME` + token | Scheduler email (production) |

## Build

```bash
npm run build
# output: ui/dist/
npm run preview   # cần API :8001
```
