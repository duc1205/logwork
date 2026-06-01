# Plan — Logwork Audit

> Chi tiết source, kiến trúc, CLI: **[TAI_LIEU_SOURCE.md](./TAI_LIEU_SOURCE.md)**

## Checklist core

- [x] Engine Lớp 1 + Lớp 2
- [x] Export MD + golden validate/compare
- [x] Mock pipeline + CSV import
- [x] Predictive, heatmap, scheduler, Teams webhook
- [x] Jira API (`LiveJiraClient` + `--live-jira`, fallback CSV)
- [x] Plugin ProjectTimesheet (`TimesheetPluginClient` + `--plugin`)
- [x] Scheduler `monthly_close` → `run_month`
- [x] Heatmap viewer HTML (`output/heatmap_viewer.html`)
- [ ] Golden file QA đầy đủ (CSV + input cùng kỳ từ QA thật)

## Checklist Web UI + API

- [x] FastAPI: auth, summary, notifications, scheduler
- [x] React: login, dashboard, notifications
- [x] Login Jira + plugin fetch theo creds user
- [x] PeriodPicker: tuần (Từ–Đến) + tháng
- [x] Ẩn ngày tương lai (`as_of`)
- [x] Admin: toàn team qua plugin
- [x] Bù trừ Lớp 2 trên dashboard (`compensation_pairs`)
- [x] Heatmap page (API `/dashboard/heatmap` + React grid)
- [x] Predictive alerts (API `/dashboard/predictive` + banner T2/T3)
- [x] Chỉ dữ liệu Jira live — API tách `fixtures/live`, không đọc `fixtures/mock`
- [x] QA: đối soát team từ ProjectTimesheet (mọi NV có log)
- [x] Export CSV summary + compensation (API + UI, format golden)
- [x] Lọc QA: `LOGWORK_TEAM`, `LOGWORK_CENTER`, `LOGWORK_ROSTER_ONLY`
- [x] Notification cache chỉ batch Jira + purge UI
- [x] Job nhắc: gửi email SMTP tới NV vi phạm/thiếu log (Jira email + roster)
- [x] Scheduler auto 17:00 thứ Tư (APScheduler + log/state + UI lịch chạy)
- [x] Admin UI: cấu hình penalty_per_md + ngày nghỉ lễ (API + fixtures/live)
- [x] Quy tắc OT: ValidMax, trần ngày, grace, chấp nhận log T7/CN/lễ/phép + đăng ký OT
- [x] Account search picker (Jira + roster fallback) cho form OT
- [x] Phân quyền: QA (`LOGWORK_QA_USERS`) vs admin cấu hình (`LOGWORK_ADMIN_USERS`)
- [x] UX tải team QA (không block trang, banner chờ Jira)
- [x] UI polish: period dùng chung, mobile nav, heatmap drill-down, lọc team/thông báo
- [ ] Golden QA với file CSV thật từ team QA (chờ dữ liệu)
