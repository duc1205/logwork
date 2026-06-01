# Cấu hình live (API / Web UI)

Thư mục này **không chứa dữ liệu mock**. API chỉ đọc:

| File | Mục đích |
|------|----------|
| `config.json` | Giờ, phạt MD, predictive, **`ot_rules`** (trần OT, grace, cho phép log T7/lễ/phép) |
| `holidays.json` | Ngày lễ công ty |
| `overtime.json` | OT approved/pending (QA đăng ký thủ công) || `employees.csv` | Roster QA tùy chọn (account Jira, Target MD, Team) |

Worklog và nghỉ phép cá nhân lấy **100% từ Jira** (ProjectTimesheet + Effort/Holiday plugin).

Override đường dẫn: `LOGWORK_DATA_DIR=/path/to/live`

Dữ liệu mock cho test CLI: `fixtures/mock/` — **API không đọc**.
