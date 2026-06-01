# Logwork Audit System

Hệ thống rule-based đối soát logwork Jira (Đề bài số 5).

**Tài liệu đầy đủ (giải thích source, CLI, nghiệp vụ):** [TAI_LIEU_SOURCE.md](./TAI_LIEU_SOURCE.md)

## Quick start

```bash
python -m logwork test
python -m logwork reconcile --remind --heatmap --predict
python -m logwork reconcile --month 2026-05
python -m logwork schedule --job monthly_close --month 2026-05
```

## Chia sẻ trong công ty (LAN test)

```powershell
cd d:\TINHVAN\HVKHQS-AI
.\logwork\scripts\run_lan.ps1
```

Gửi link `http://<IP-máy-bạn>:5173/` cho đồng nghiệp cùng WiFi/VPN. Chi tiết: [ui/README.md](./ui/README.md)

## Web UI (React)

```bash
# Chỉ localhost
.\logwork\scripts\run_dev.ps1

# Hoặc thủ công:
pip install -r logwork/requirements-api.txt
cd d:\TINHVAN\HVKHQS-AI
$env:LOGWORK_DISABLE_SCHEDULER="1"
python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port 8000 --reload

cd logwork/ui && npm install && npm run dev
```

- Login: **username + password Jira** (jira.tinhvan.com) — **100% dữ liệu Jira**, không mock
- Phân quyền (env server, **không** phải Administrator Jira):
  - **employee** — chỉ dữ liệu cá nhân (mặc định)
  - **QA** (`LOGWORK_QA_USERS`) — đối soát team, golden, job nhắc
  - **cấu hình** (`LOGWORK_ADMIN_USERS`) — QA + trang Cấu hình
- Cấu hình: `fixtures/live/` (config, ngày lễ, roster CSV tùy chọn)
- Dashboard: lấy logwork thật qua **ProjectTimesheet plugin** + nghỉ phép từ **Effort/Holiday**
- Chọn kỳ: **theo tuần** (Từ ngày → Đến ngày T2–CN) hoặc **theo tháng** (01 → cuối tháng)
- **Export CSV** summary/compensation (format golden QA)
- **Cấu hình** (admin): mức phạt/MD, ngày nghỉ lễ, **quy tắc OT** + đăng ký OT duyệt — lưu `fixtures/live/`
- **Job nhắc (17h T4)**: tự chạy qua APScheduler · gửi email SMTP — cấu hình `JIRA_USERNAME` + `LOGWORK_SMTP_*` trên server (dev: `LOGWORK_DISABLE_SCHEDULER=1`)

Chi tiết: [ui/README.md](./ui/README.md)
