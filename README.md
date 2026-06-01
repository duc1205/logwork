# Logwork Audit System

Hệ thống rule-based đối soát logwork Jira (Đề bài số 5).

**Repo GitLab:** https://gitlabtv.tinhvan.com/tvs-tinhvan-solution/tvs/tvh-ai/jira-report

**Hướng dẫn chạy trên máy local:** [docs/CHAY_LOCAL.md](./docs/CHAY_LOCAL.md)

**Tài liệu source / nghiệp vụ:** [TAI_LIEU_SOURCE.md](./TAI_LIEU_SOURCE.md)

## Quick start (CLI)

```bash
python -m logwork test
python -m logwork reconcile --remind --heatmap --predict
python -m logwork reconcile --month 2026-05
python -m logwork schedule --job monthly_close --month 2026-05
```

> Lệnh `python -m logwork` cần thư mục repo tên **`logwork`** và chạy lệnh từ **thư mục cha** (vd. `d:\`). Xem [docs/CHAY_LOCAL.md](./docs/CHAY_LOCAL.md).

## Web UI (nhanh nhất)

```powershell
cd d:\
.\logwork\scripts\run_dev.ps1
```

Mở http://localhost:5173 — đăng nhập username + mật khẩu Jira.

## Chia sẻ trong LAN (đồng nghiệp test)

```powershell
cd d:\
.\logwork\scripts\run_lan.ps1
```

Gửi link `http://<IP-máy-bạn>:5173/`. Chi tiết: [ui/README.md](./ui/README.md)

## Tính năng chính

- Login Jira live (jira.tinhvan.com), worklog qua ProjectTimesheet
- Phân quyền server: `LOGWORK_QA_USERS`, `LOGWORK_ADMIN_USERS`
- Dashboard tuần/tháng, heatmap, golden QA, export CSV, cấu hình OT/phạt MD
- Job nhắc 17h T4 (tắt khi dev: `LOGWORK_DISABLE_SCHEDULER=1`)
