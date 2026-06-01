# Chia sẻ UI qua GitHub Pages

**Link công khai (sau khi bật Pages):** https://duc1205.github.io/logwork/

## Bước 1 — Bật GitHub Pages (một lần)

1. Mở https://github.com/duc1205/logwork/settings/pages
2. **Build and deployment** → **Source:** chọn **GitHub Actions** (không chọn Deploy from branch)
3. Lưu

## Bước 2 — Chạy deploy

- Push lên nhánh `main` → workflow **Deploy UI (GitHub Pages)** tự chạy  
- Hoặc: **Actions** → **Deploy UI (GitHub Pages)** → **Run workflow**

Đợi job xanh → mở lại link https://duc1205.github.io/logwork/

## Bước 3 — API cho mọi người (bắt buộc)

GitHub Pages **chỉ host giao diện**. Mỗi người vẫn đăng nhập Jira riêng; dữ liệu lấy qua **API FastAPI** của bạn.

### Cách A — Cloudflare Tunnel (nhanh, khuyên dùng demo)

Trên máy chạy API:

```powershell
cd d:\
$env:LOGWORK_DATA_DIR="d:\logwork\fixtures\live"
$env:LOGWORK_DISABLE_SCHEDULER="1"
python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port 8001

# Terminal khác — tunnel chỉ API
cloudflared tunnel --url http://127.0.0.1:8001
```

Copy link `https://xxxx.trycloudflare.com` (không có `/` cuối).

Rồi **một trong hai**:

| Cách | Việc cần làm |
|------|----------------|
| **GitHub Variable** | Repo → Settings → Secrets and variables → Actions → Variables → `VITE_API_BASE_URL` = `https://xxxx.trycloudflare.com` → chạy lại workflow deploy |
| **config.json** | Sửa `ui/public/config.json`: `"apiBaseUrl": "https://xxxx.trycloudflare.com"` → push `main` |

Trên server API (máy tunnel):

```powershell
$env:LOGWORK_ALLOW_LAN="1"
# hoặc
$env:LOGWORK_CORS_ORIGINS="https://duc1205.github.io"
```

### Cách B — LAN / VPN công ty

Dùng `.\logwork\scripts\run_lan.ps1` — đồng nghiệp mở `http://<IP-máy-bạn>:5173/` (không qua GitHub).

## Kiểm tra

- UI: https://duc1205.github.io/logwork/ — trang login load được
- Trang login hiển thị **API:** `https://...` (không được “Chưa cấu hình”)
- Đăng nhập username/password Jira → dashboard có dữ liệu

## Repo

https://github.com/duc1205/logwork
