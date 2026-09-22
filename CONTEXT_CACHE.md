# DrugTime — Project Handoff Context & Architectural Cache

> **Mục đích:** File lưu trữ context toàn diện cho phiên làm việc tiếp theo / background agent khác của dự án DrugTime.  
> **Trạng thái:** v2.3 FINAL (Scaffold Complete, Contract-First Verified, 18/18 Pytest Passed).  
> **Cách dùng:** Copy toàn bộ file này hoặc dán đường dẫn `@docs/CONTEXT_CACHE.md` vào prompt mở đầu phiên mới.

---

## 1. Tổng Quan Dự Án & Tech Stack

- **Tên dự án:** DrugTime — Hệ thống nhắc thuốc thông minh & kiểm soát an toàn dược lý gia đình.
- **Consumers:**
  - Mobile App (Flutter): Bệnh nhân (chế độ chuẩn & Simple Mode người cao tuổi) và Người thân (Caregiver).
  - Admin Web (Next.js 14): Quản trị viên dược, catalog, kiểm toán tuân thủ & Four-Eyes review.
- **Backend Stack:** FastAPI (Python 3.11+ / 3.14), Pydantic v2, RESTful, OpenAPI 3.1.
- **Mô hình kiến trúc:** Contract-First Modular Monolith. Mọi route trả envelope UTF-8 chuẩn `{success, data, error, message}`.
- **Cơ sở dữ liệu đích:** PostgreSQL (Supabase). Giao tiếp hoàn toàn qua FastAPI (`/api/v1/*`), client không truy cập trực tiếp database.

---

## 2. Tiêu Chuẩn Pháp Lý & Ràng Buộc Y Tế Cốt Lõi

1. **Nghị định 356/2025/NĐ-CP (Bảo vệ dữ liệu cá nhân Việt Nam):**
   - **Consent tracking:** Lưu vết lịch sử append-only cho 3 mục đích độc lập: `health_data`, `family_sharing`, `ai_meal`. Rút `health_data` thì khóa truy cập; rút `family_sharing` thì ngắt chia sẻ người thân.
   - **Data Portability:** `POST /api/v1/users/me/data-export` trả `202 Accepted` kèm `job_id`; poll qua `GET .../jobs/{job_id}` lấy link tải file ZIP/JSON (hạn 24h).
   - **Quyền được xóa:** `POST /api/v1/data-deletion-requests` tiếp nhận yêu cầu, Admin duyệt thủ công qua `POST /admin/data-deletion-requests/{id}/process`.
2. **Nguyên tắc An Toàn Y Tế (NFR01–NFR07, QA.04):**
   - **0% LLM trong an toàn thuốc:** Rule Engine kiểm tra tương tác thuốc-thuốc (Bảng C), thuốc-thực phẩm (Bảng D), thuốc-bệnh nền (Bảng E) là **deterministic thuần túy (Rule-based)**, không dùng AI/LLM.
   - **Tự động kích hoạt phân tích:** Mọi thay đổi ở thuốc (`user_medications`) hoặc bệnh nền (`user_conditions`) đều tự động sinh `regimen_analysis_snapshots` và cập nhật findings.
   - **Trách nhiệm pháp lý xác nhận khuyến nghị:** `PATCH /api/v1/recommendations/{id}/acknowledge` **chỉ cho phép duy nhất bệnh nhân (`self`)**, cấm người thân và Admin làm thay.
   - **Bảo tồn lịch sử y khoa:** Toàn bộ dữ liệu lâm sàng (`conditions`, `prescriptions`, `user-medications`, `schedules`) chỉ được **Soft-Delete** (`trang_thai: 'archived'`). HTTP DELETE chuẩn RESTful không body (`Path: id`).

---

## 3. Ma Trận Phân Quyền & Kiến Trúc Giám Sát Kép (Dual Supervision)

### 3.1. Ma trận RBAC cuối cùng
| Thao tác (Operation) | Self (Bệnh nhân) | Family Read | Family Write | Admin |
|---|:---:|:---:|:---:|:---:|
| **Xem hồ sơ y tế bệnh nhân** | ✅ | ✅ | ✅ | ✅ *(Theo audit policy)* |
| **Kê đơn / Sửa thuốc / Sửa lịch** | ✅ | ❌ | ✅ | ⚠️ `admin_override` + `X-Admin-Reason` |
| **Xóa mềm dữ liệu lâm sàng** | ✅ | ❌ | ✅ | ⚠️ `admin_override` + `X-Admin-Reason` |
| **Upload OCR xem trước (preview)** | ✅ | ✅ | ✅ | ✅ *(Quyền READ, Max 10MB)* |
| **Phân tích phác đồ tương tác** | ✅ | ✅ | ✅ | ✅ *(Hàm thuần, quyền READ)* |
| **Xác nhận đọc khuyến nghị** | ✅ | ❌ | ❌ | ❌ *(Chỉ duy nhất bệnh nhân)* |
| **Thu hồi liên kết Caregiver** | ✅ | ❌ | ❌ | ⚠️ Emergency Override + Four-Eyes ≤ 24h |
| **Mở rộng quyền Caregiver** | ✅ | ❌ | ❌ | ❌ *(Cấm tuyệt đối Admin)* |
| **Hậu kiểm can thiệp khẩn cấp** | ❌ | ❌ | ❌ | ✅ *(Bắt buộc Admin B != Admin A)* |

### 3.2. Header dùng chung `X-Admin-Reason`
- Quản trị viên can thiệp vào dữ liệu bệnh nhân (`admin_override`) bắt buộc phải truyền header:
  `X-Admin-Reason: <string>` (tối thiểu 10 ký tự, hỗ trợ plain ASCII hoặc URL-encoded UTF-8).
- Thiếu hoặc < 10 ký tự → FastAPI dependency từ chối ngay với HTTP `422 ADMIN_OVERRIDE_REASON_REQUIRED`.
- Lý do can thiệp tự động ghi vào `ly_do_can_thiep` trong `access_logs`.

### 3.3. Phân biệt mức giám sát Dual Supervision
- **Clinical Admin Override:** Bắt buộc `X-Admin-Reason` + Audit Log + Tự động chạy Rule Engine re-analysis tạo snapshot. Không cần Four-Eyes ở Phase 1.
- **Caregiver Emergency Override (`PATCH /caregivers/{link_id}`):**
  - Admin **chỉ được thu hẹp hoặc thu hồi quyền** (vi phạm mở rộng trả `403 CANNOT_EXPAND_PERMISSIONS_AS_ADMIN`).
  - Tự động đẩy notification in-app cho bệnh nhân.
  - Tạo audit entry với `is_emergency_override: true`, `review_status: 'pending_post_review'`, `review_deadline = created_at + 24h`.
  - **Bắt buộc Four-Eyes hậu kiểm ≤ 24h**.

### 3.4. Four-Eyes Post-Review (`POST /api/v1/admin/audit-logs/{id}/post-review`)
- Request: `{"decision": "valid" | "invalid", "review_note": "..."}` (note 10–2000 ký tự).
- 3 trạng thái: `pending_post_review`, `reviewed_valid`, `reviewed_invalid`.
- 5 Guardrails:
  1. `actor_role == admin` (vi phạm: `403 INSUFFICIENT_ADMIN_PERMISSION`).
  2. `reviewer_user_id != audit_log.actor_user_id` (vi phạm: `403 CANNOT_REVIEW_OWN_ACTION`).
  3. `audit_log.is_emergency_override == true` (vi phạm: `409 REVIEW_NOT_REQUIRED`).
  4. `audit_log.review_status == 'pending_post_review'` (vi phạm: `409 REVIEW_ALREADY_COMPLETED`).
  5. `now <= audit_log.review_deadline` (vi phạm: `409 POST_REVIEW_DEADLINE_EXCEEDED`).
- Nếu `decision == 'invalid'`:
  - Gắn cờ `COMPLIANCE_REVIEW_REQUIRED` vào bản ghi.
  - Gửi thông báo vi phạm cho nhóm pháp chế / compliance.
  - **Tuyệt đối KHÔNG tự động khôi phục quyền caregiver** (phải qua action nghiệp vụ riêng).
- Sinh thêm audit event độc lập (#1002) ghi vết hành vi hậu kiểm (`action: 'POST_REVIEW'`).

---

## 4. Caregiver Link Code & OCR Constraints

1. **Vòng đời mã Caregiver (Điểm 15, 23):**
   - Mã 6 số / QR là **Multi-use trong hạn 15 phút** (phục vụ nhiều con cùng kết nối vào tài khoản cha mẹ).
   - Tự động hết hạn khi: quá 15 phút, bệnh nhân sinh mã mới (mã cũ chuyển `expired`), hoặc bị nhập sai > 10 lần toàn cục (`400 LINK_CODE_INVALIDATED`).
   - Rate-limit theo caller/IP: tối đa 5 lần thử sai / 15 phút (`429 LINK_CODE_RATE_LIMITED`).
2. **OCR Blister Upload (`POST /patients/{id}/prescriptions/ocr-upload`):**
   - Quyền: `read` (preview xem trước, không lưu DB, không sinh rác catalog).
   - Giới hạn: Max 10MB. MIME whitelist: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`. Vi phạm trả `422`.

---

## 5. Cấu Trúc Mã Nguồn & Bản Đồ Files

```text
e:/DrugTIme_main/
├── docs/
│   ├── API_DESIGN.md              # Đặc tả chi tiết 64 endpoints (v2.3 FINAL)
│   ├── CHANGES_FROM_SPEC.md       # Bảng đối chiếu 27 điểm thay đổi so với spec gốc
│   ├── CONTEXT_CACHE.md           # [FILE NÀY] Cache context bàn giao giữa các phiên
│   └── openapi.json               # OpenAPI 3.1 JSON export đồng bộ
├── backend/
│   ├── main.py                    # Entrypoint khởi chạy dev server
│   ├── openapi.json               # OpenAPI export tại backend
│   ├── requirements.txt           # fastapi, uvicorn, pydantic, pytest, python-multipart
│   ├── README.md                  # Hướng dẫn chạy và bảng đối chiếu route
│   ├── app/
│   │   ├── main.py                # FastAPI app setup, CORS, route registration
│   │   ├── mock_db.py             # In-memory mock database fixture singleton (`db`)
│   │   ├── core/
│   │   │   ├── security.py        # Token mock authentication & user role resolution
│   │   │   ├── access_control.py  # RBAC, audit logging & header X-Admin-Reason enforcement
│   │   │   └── rate_limit.py      # Sliding window limiter & CodeFailureTracker
│   │   ├── schemas/               # Pydantic v2 schemas theo 9 nhóm chức năng
│   │   │   ├── common.py          # ResponseEnvelope, MessageResponse, PaginatedData
│   │   │   ├── auth.py            # User profile, device token, async data export
│   │   │   ├── consents.py        # Consents & Data deletion requests (NĐ 356)
│   │   │   ├── conditions.py      # Catalog & user medical conditions
│   │   │   ├── prescriptions.py   # Medications, OCR upload, prescriptions
│   │   │   ├── schedules.py       # Schedules, batch dose sync per-item
│   │   │   ├── safety.py          # Regimen snapshots, findings, quick-check
│   │   │   ├── caregivers.py      # Link codes, caregiver links, notifications
│   │   │   ├── meals.py           # Async AI meal suggestions
│   │   │   └── admin.py           # Catalog CRUD, rule_change_logs, four-eyes post-review
│   │   └── routers/               # 9 routers tương ứng 9 nhóm chức năng
│   └── tests/
│       └── test_api_endpoints.py  # 18 test cases TDD bao phủ toàn bộ spec & RBAC
```

---

## 6. Danh Sách Tài Khoản Mock Đang Có Trong Test

Truyền qua HTTP Header `Authorization: Bearer <user_id>`:
- `usr-patient-1`: Bệnh nhân mẫu (Simple Mode bật, consents đầy đủ).
- `usr-family-1`: Người thân có quyền Xem + Ghi (`cho_phep_chinh_sua: true`).
- `usr-family-readonly`: Người thân chỉ có quyền Xem (`cho_phep_chinh_sua: false`).
- `usr-admin-1`: Quản trị viên A (thực hiện can thiệp khẩn cấp).
- `usr-admin-2`: Quản trị viên B độc lập (thực hiện Four-Eyes post-review `CANNOT_REVIEW_OWN_ACTION`).

---

## 7. Các Lệnh Kiểm Thử & Chạy Nhanh

```bash
# 1. Chạy toàn bộ 18 test cases
cd backend
python -m pytest tests/ -v

# 2. Chạy Dev server và xem Swagger UI
python main.py
# URL: http://localhost:8000/docs | ReDoc: http://localhost:8000/redoc

# 3. Re-export OpenAPI spec khi sửa schema
python -c "import json, shutil; from app.main import app; schema = app.openapi(); open('openapi.json', 'w', encoding='utf-8').write(json.dumps(schema, indent=2, ensure_ascii=False)); shutil.copyfile('openapi.json', '../openapi.json'); shutil.copyfile('openapi.json', '../docs/openapi.json')"
```

---

## 8. Hướng Dẫn Tiếp Tục Triển Khai (Next Phase Roadmap)

Khi phiên tiếp theo bắt đầu viết logic thật:
1. **Database Layer:** Thay thế `app/mock_db.py` bằng SQLAlchemy/SQLModel async engine (`asyncpg`) kết nối Supabase Postgres, tạo migrations bằng Alembic.
2. **Auth Integration:** Thay hàm mock `get_current_user` trong `app/core/security.py` bằng Supabase Auth JWT verification (decode RSA public key từ Supabase JWKS).
3. **Deterministic Rule Engine (QA.04):** Triển khai logic kiểm tra tương tác thuốc thuần Python/SQL cho 4 bảng A-D (không gọi LLM).
4. **OCR Pipeline:** Tích hợp Google ML Kit on-device (Flutter) và pipeline backend fallback OCR trong `upload_prescription_ocr`.
5. **LLM Meal Suggestions:** Tích hợp worker bất đồng bộ (Celery / Arq / FastAPI BackgroundTasks) gọi Gemini API với prompt dinh dưỡng y khoa.
6. **Scheduled Compliance Worker:** Thiết lập cron định kỳ quét các bản ghi `pending_post_review` quá 24h để gắn cờ `POST_REVIEW_OVERDUE`.
