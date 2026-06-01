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
# Chỉ localhost (mở 2 cửa sổ API + UI)
.\logwork\scripts\run_dev.ps1

# Hoặc thủ công (repo tại d:\logwork → chạy từ thư mục cha d:\):
pip install -r logwork/requirements-api.txt
cd d:\
$env:LOGWORK_DISABLE_SCHEDULER="1"
$env:LOGWORK_DATA_DIR="d:\logwork\fixtures\live"
python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port 8000 --reload

cd logwork/ui && npm install && npm run dev
```

Nếu dashboard báo **Internal Server Error**: kiểm tra `GET /api/health` → `data_dir` phải trỏ tới thư mục có `config.json` (vd. `d:\logwork\fixtures\live`). Biến môi trường `LOGWORK_DATA_DIR` cũ (path `TINHVAN` đã xóa) sẽ gây lỗi — xóa trong Windows env hoặc để script `run_dev.ps1` ghi đè.

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

## UI trên GitHub Pages

Workflow [`.github/workflows/deploy-ui.yml`](./.github/workflows/deploy-ui.yml) publish UI tại **https://duc1205.github.io/logwork/**

1. Repo → **Settings** → **Pages** → Source: **GitHub Actions**
2. **Actions** → **Variables** → `VITE_API_BASE_URL` = URL FastAPI public (bắt buộc)
3. Server API: `LOGWORK_ALLOW_LAN=1` hoặc `LOGWORK_CORS_ORIGINS` có `https://duc1205.github.io`

Pages chỉ host UI tĩnh — API uvicorn chạy riêng (tunnel/VPS).
