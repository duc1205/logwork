# Logwork UI (React)

Giao diện web cho hệ thống đối soát logwork — gọi API tại `logwork/api/`.

## Chạy dev (localhost)

**Terminal 1 — API backend:**

```bash
cd d:\TINHVAN\HVKHQS-AI
pip install -r logwork/requirements-api.txt
set LOGWORK_DISABLE_SCHEDULER=1
python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — React UI:**

```bash
cd logwork/ui
npm install
npm run dev
```

Mở http://localhost:5173

## Chia sẻ LAN — đồng nghiệp trong công ty test

Trên **máy làm server** (PowerShell Admin nếu cần mở firewall):

```powershell
cd d:\TINHVAN\HVKHQS-AI
.\logwork\scripts\run_lan.ps1
```

Script hiện IP LAN và link `http://192.168.x.x:5173/`. Đồng nghiệp cùng mạng/VPN mở link đó, đăng nhập Jira riêng.

| Port | Dịch vụ |
|------|---------|
| 5173 | UI (Vite, `--host 0.0.0.0`) |
| 8000 | API (uvicorn `--host 0.0.0.0`) |

UI proxy `/api` về API local — người test **chỉ cần port 5173**.

Thủ công:

```bash
# API
set LOGWORK_ALLOW_LAN=1
python -m uvicorn logwork.api.main:app --host 0.0.0.0 --port 8000 --reload

# UI
cd logwork/ui && npm run dev:lan
```

## PC cáp mạng — không có Mobile Hotspot

Laptop WiFi thường **không tới** IP dây `10.2.0.x`. Nếu không dùng hotspot, chọn một trong các cách:

| Cách | Khi nào dùng |
|------|----------------|
| **VPN công ty** | Đồng nghiệp bật VPN → thử lại `http://10.2.0.6:5173/` |
| **Cắm dây LAN** | Cùng switch/VLAN với PC server |
| **Cloudflare Tunnel** | Khác mạng, có internet, demo nhanh |

### Cloudflare Tunnel (khuyên dùng khi LAN fail)

```powershell
winget install Cloudflare.cloudflared
cd d:\TINHVAN\HVKHQS-AI
.\logwork\scripts\run_tunnel.ps1
```

Copy link `https://....trycloudflare.com` gửi đồng nghiệp. Mỗi người vẫn login Jira riêng.

*Một số công ty chặn `trycloudflare.com` — khi đó nhờ IT mở route LAN hoặc deploy lên server nội bộ chung.*

## Đăng nhập

Dùng **username + mật khẩu Jira** của chính bạn (cùng tài khoản [jira.tinhvan.com](https://jira.tinhvan.com)).

API xác thực qua `GET /rest/api/2/myself` — **chỉ tài khoản Jira thật**, không mock/demo.

| Field | Ví dụ |
|-------|-------|
| Username | `ducnm1` |
| Password | Mật khẩu Jira của bạn |

Cấu hình live: `logwork/fixtures/live/` (config, holidays, roster CSV). Mock chỉ dùng cho `python -m logwork test`.

## Tính năng

- **Login** — xác thực Jira account (live only)
- **Tổng hợp tuần / tháng** — chọn kỳ với ngày bắt đầu và kết thúc rõ ràng
  - Tuần: ô **Từ ngày** + **Đến ngày** (Chủ nhật, tự tính), nút tuần trước/sau
  - Tháng: chọn tháng, hiển thị `01/MM/YYYY → cuối tháng`
- Actual/Required/Missed MD, phạt, chi tiết từng ngày (ẩn ngày chưa tới)
- **Bù trừ Lớp 2** — bảng cặp ngày thiếu/bù trên dashboard
- **Heatmap** (`/heatmap`) — lưới màu NV × ngày; admin xem toàn team
- **Predictive** — banner cảnh báo pace T2/T3 trên dashboard
- **Golden QA** (`/admin/golden`) — admin upload CSV golden, so khớp engine
- **Cấu hình** (`/admin/settings`) — mức phạt/MD, ngày nghỉ lễ, quy tắc OT, đăng ký OT duyệt
- **Export CSV** — summary + compensation (format golden, clip `as_of`)
- **Thông báo** — nhắc vi phạm cá nhân (batch sinh lúc **17:00 thứ Tư**); **Chạy job nhắc** gửi email SMTP tới NV thiếu/vi phạm
- **Admin** — xem toàn team, trigger job nhắc thủ công, golden compare

### Env QA (tùy chọn)

| Biến | Mô tả |
|------|--------|
| `LOGWORK_QA_USERS` | Account Jira có quyền admin/QA |
| `LOGWORK_PROJECT_KEYS` | Lọc project (`*` = tất cả) |
| `LOGWORK_ROSTER_ONLY=1` | Chỉ NV trong `employees.csv` |
| `LOGWORK_TEAM` / `LOGWORK_CENTER` | Lọc roster theo team/center |
| `JIRA_USERNAME` + `JIRA_API_TOKEN` | Scheduler 17h T4 (nếu không trigger thủ công) |
| `LOGWORK_SMTP_HOST`, `LOGWORK_SMTP_USER`, `LOGWORK_SMTP_PASSWORD`, `LOGWORK_EMAIL_FROM` | Gửi email nhắc khi chạy job (admin hoặc scheduler) |

### Query API (dashboard / notifications)

| Chế độ | Query |
|--------|-------|
| Tuần | `?start=YYYY-MM-DD&end=YYYY-MM-DD` |
| Tháng | `?month=YYYY-MM` |
| Legacy | `?week=YYYY-MM-DD` (ngày bất kỳ trong tuần) |
| Heatmap | `GET /api/dashboard/heatmap` — cùng query kỳ |

## Cấu trúc

```
ui/
├── src/
│   ├── api/          # client + types
│   ├── context/      # AuthContext (JWT)
│   ├── components/   # Layout, PeriodPicker, StatCard, DailyTable, …
│   └── pages/        # Login, Dashboard, Notifications
├── vite.config.ts    # proxy /api → :8000
└── package.json
```

## Build production

```bash
npm run build
# output: ui/dist/
```
