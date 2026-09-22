# DrugTime — Kế hoạch & Đặc tả Thiết kế Toàn bộ API Endpoint Frontend (Bản Chốt)

> **Dự án:** DrugTime MVP (Nền tảng Quản lý & Nhắc nhở Dùng thuốc An toàn)  
> **Khách hàng API:** 📱 Mobile App (Flutter) & 💻 Admin Web (Next.js)  
> **Cơ sở thiết kế:** Schema Cơ sở Dữ liệu v2, Luật BV Dữ liệu Cá nhân 2025 & NĐ 356/2025/NĐ-CP, Kiến trúc Container & Bảng phân bổ QA.

---

## ⚡ Tóm tắt Điều hành (Executive Summary cho ADHD)

| Trọng tâm | Quyết định cốt lõi | Lý do kỹ thuật |
|---|---|---|
| **Cổng giao tiếp duy nhất** | Frontend (Mobile/Admin) **chỉ gọi FastAPI** (`/api/v1/*`), không kết nối trực tiếp Supabase. | Giữ Supabase RLS an toàn, đảm bảo kiểm tra consent và ghi `access_logs` (NFR06). |
| **Phân quyền theo ngữ cảnh** | Role được tính theo từng request (`self`, `family`, `admin`), không lưu cứng trên user. | Người dùng vừa có thể là Bệnh nhân tự quản lý, vừa là Người thân giám sát cha mẹ. |
| **Offline-First & Idempotent** | Mobile dùng Local Notification; Sync lịch sử uống thuốc qua batch endpoint với `client_uuid`. | Chống ghi trùng liều khi mạng chập chờn hoặc retry (QA.05, QA.08). |
| **Tương tác thuốc xác định** | Kiểm tra tương tác thuốc-thuốc/thức ăn/bệnh là **Rule-based thuần túy**, 0% LLM. | Đảm bảo tính nhất quán y khoa, có thể kiểm thử hồi quy 100% (QA.04). |
| **Bảo vệ dữ liệu cá nhân** | Đồng thuận tách rời (`health_data`, `family_sharing`, `ai_meal`), lưu vết truy cập append-only. | Tuân thủ triệt để NĐ 356/2025/NĐ-CP và NFR01. |

> **Lazier Alternative:** Cho Mobile gọi thẳng Supabase PostgREST qua Supabase Client SDK với RLS policy.  
> *Đánh giá:* Nhanh hơn 1 ngày dựng API, nhưng **phá vỡ audit log tự động (QA.09)**, làm lộ logic kiểm tra tương tác ra ngoài, và khó xử lý quy tắc tính liều phối hợp. **FastAPI Gateway là mức tối thiểu an toàn.**

---

## 🛠️ Quy chuẩn Kỹ thuật Giao tiếp (API Conventions)

- **Base URL:** `https://api.drugtime.vn/api/v1` (Dev: `http://localhost:8000/api/v1`)
- **Định dạng:** JSON (UTF-8), URL `kebab-case`, danh từ số nhiều (RESTful).
- **Header xác thực:** `Authorization: Bearer <Supabase_JWT_Token>`
- **Chuẩn cấu trúc Response:**
  ```json
  // Thành công:
  {
    "success": true,
    "data": { ... },
    "message": "Thao tác thành công"
  }

  // Lỗi:
  {
    "success": false,
    "data": null,
    "error": {
      "code": "FAMILY_CONSENT_REVOKED",
      "message": "Bệnh nhân đã thu hồi quyền chia sẻ dữ liệu cho người thân.",
      "details": []
    }
  }
  ```
- **Chuẩn Phân trang:**
  ```json
  {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 45,
      "total_pages": 3
    }
  }
  ```

---

## 🔐 Cơ chế Phân quyền Ngữ cảnh (Contextual Access Control Interceptor)

Mọi request truy cập tài nguyên của bệnh nhân `{patient_id}` đều đi qua Dependency `verify_patient_access`:

```
Caller C gọi endpoint với target patient P:
├── C == P
│   └── Kiểm tra consent "health_data" của P còn hiệu lực?
│       ├── CÓ  --> actor_role = 'self' (Cho phép)
│       └── KHÔNG --> 403 (Cần cấp consent trước khi truy cập)
│
├── C != P
│   ├── C.vai_tro_he_thong == 'admin' --> actor_role = 'admin' (Cho phép + Bắt buộc ghi log)
│   └── Tồn tại caregiver_links(patient=P, family=C, trang_thai='active', cho_phep_chia_se=true)
│       VÀ consent "family_sharing" của P còn hiệu lực?
│       ├── CÓ  --> actor_role = 'family' (Cho phép)
│       └── KHÔNG --> 403 (Không có quyền hoặc bệnh nhân đã thu hồi chia sẻ)
│
└── Không thuộc các trường hợp trên --> 403 Forbidden
└── [LUÔN THỰC HIỆN]: Ghi bản ghi vào bảng access_logs (bất kể allowed hay denied).
```

---

## 📋 Danh mục Toàn bộ API Endpoints cho Frontend

### 1. Nhóm Auth & Người dùng (Identity & Profile)
*Áp dụng: 📱 Mobile Flutter & 💻 Admin Web*

| HTTP Method | Endpoint | Mục đích cho Frontend | Request Body / Query Params | Response Data chính |
|---|---|---|---|---|
| `POST` | `/auth/sync-profile` | Đồng bộ thông tin user từ Supabase Auth sang bảng `users` | `{ ho_ten, so_dien_thoai, ngay_sinh, gioi_tinh }` | `User` object |
| `GET` | `/users/me` | Lấy profile người dùng hiện tại & cài đặt | — | Profile, `che_do_nguoi_cao_tuoi`, `vai_tro_he_thong` |
| `PATCH` | `/users/me` | Cập nhật profile, bật/tắt Simple Mode (`che_do_nguoi_cao_tuoi`) | `{ ho_ten?, che_do_nguoi_cao_tuoi? }` | `User` cập nhật |
| `POST` | `/users/me/device-tokens` | Đăng ký FCM token của thiết bị để nhận cảnh báo | `{ fcm_token: string, platform: 'android' \| 'ios' }` | Trạng thái đăng ký |
| `DELETE` | `/users/me/device-tokens/{fcm_token}` | Xóa token khi đăng xuất | — | Trạng thái hủy |

---

### 2. Nhóm Đồng thuận & Quyền Riêng tư (Consent & Privacy — NĐ 356)
*Áp dụng: 📱 Mobile Flutter (FR01, FR09, NFR01)*

| HTTP Method | Endpoint | Mục đích cho Frontend | Request Body / Query Params | Response Data chính |
|---|---|---|---|---|
| `GET` | `/consents/me` | Lấy danh sách đồng thuận hiện tại theo từng mục đích | — | Array các consent (`health_data`, `family_sharing`, `ai_meal`) |
| `POST` | `/consents` | Cấp mới hoặc thu hồi đồng thuận (Append-only vào `user_consents`) | `{ loai_dong_y: string, trang_thai: 'dong_y' \| 'thu_hoi', phien_ban_van_ban: string }` | Bản ghi consent mới |
| `POST` | `/data-deletion-requests` | Gửi yêu cầu xóa toàn bộ dữ liệu cá nhân hoặc rút consent | `{ loai: 'xoa_du_lieu' \| 'rut_consent', loai_dong_y?: string }` | Mã yêu cầu, trạng thái `cho_duyet` |
| `GET` | `/data-deletion-requests/me` | Theo dõi tiến độ yêu cầu xóa dữ liệu của mình | — | Trạng thái (`cho_duyet`, `da_duyet`, `tu_choi`) |

---

### 3. Nhóm Hồ sơ Sức khỏe & Bệnh lý nền (Conditions)
*Áp dụng: 📱 Mobile Flutter (FR04)*

| HTTP Method | Endpoint | Mục đích cho Frontend | Request Body / Query Params | Response Data chính |
|---|---|---|---|---|
| `GET` | `/conditions` | Tra cứu danh mục bệnh chuẩn hóa (tiểu đường, suy thận, hen,...) | Query: `q`, `limit` | Danh sách điều kiện y khoa chuẩn |
| `GET` | `/patients/{patient_id}/conditions` | Lấy danh sách bệnh nền của bệnh nhân | Path: `patient_id` | Array `user_conditions` kèm chi tiết phân độ/subtype |
| `POST` | `/patients/{patient_id}/conditions` | Thêm bệnh lý nền vào hồ sơ | `{ condition_id, subtype?, phan_do? }` | Bản ghi bệnh nền đã tạo |
| `DELETE` | `/patients/{patient_id}/conditions/{id}` | Xóa bệnh lý nền khỏi hồ sơ | Path: `id` | Xóa thành công |

---

### 4. Nhóm Đơn thuốc & Thuốc (Prescriptions & Medications)
*Áp dụng: 📱 Mobile Flutter (FR02, FR04)*

| HTTP Method | Endpoint | Mục đích cho Frontend | Request Body / Query Params | Response Data chính |
|---|---|---|---|---|
| `GET` | `/medications/search` | Tìm kiếm danh mục thuốc (gợi ý khi nhập tay hoặc đối chiếu sau OCR) | Query: `q=...` (tên thuốc / hoạt chất) | List thuốc từ catalog quốc gia |
| `GET` | `/medications/{id}` | Xem chi tiết 1 loại thuốc (hàm lượng, dạng bào chế, hoạt chất Bảng A) | Path: `id` | Chi tiết thuốc và hoạt chất đi kèm |
| `POST` | `/medications/unmatched-scans` | Ghi nhận chuỗi OCR blister không khớp catalog (R-01) để Admin duyệt | `{ chuoi_nhan_dien: string }` | ID bản ghi log |
| `GET` | `/patients/{patient_id}/prescriptions` | Lấy danh sách đơn thuốc của bệnh nhân | Query: `trang_thai` (`dang_dung` \| `da_ket_thuc`) | Danh sách đơn thuốc kèm thuốc con |
| `POST` | `/patients/{patient_id}/prescriptions` | Tạo đơn thuốc mới (nguồn `ocr_scan` hoặc `thu_cong`) | `{ nguon_nhap, ngay_ke_don, noi_ke_don, medications: [...] }` | Đơn thuốc mới tạo |
| `GET` | `/prescriptions/{id}` | Lấy chi tiết đơn thuốc | Path: `id` | Chi tiết đơn và danh sách thuốc |
| `PATCH` | `/prescriptions/{id}/status` | Đánh dấu kết thúc đơn thuốc (`trang_thai: da_ket_thuc`) | `{ trang_thai: 'da_ket_thuc' }` | Đơn thuốc cập nhật |
| `POST` | `/prescriptions/{id}/medications` | Bổ sung thêm thuốc vào đơn hiện hữu | `{ medication_id?, ten_thuoc_tu_nhap?, cach_nhap, so_luong_moi_lan, so_lan_moi_ngay }` | Thuốc mới tạo trong đơn |
| `PATCH` | `/user-medications/{id}` | Chỉnh sửa liều lượng hoặc xác nhận thông tin sau OCR | `{ so_luong_moi_lan?, so_lan_moi_ngay?, trang_thai_xac_nhan? }` | Bản ghi thuốc đã cập nhật |
| `DELETE` | `/user-medications/{id}` | Xóa thuốc khỏi đơn | Path: `id` | Xóa thành công |

---

### 5. Nhóm Lịch Uống & Ghi Nhận Liều (Schedules & Idempotent Dose Logging)
*Áp dụng: 📱 Mobile Flutter (FR03, QA.05, QA.08 - Local Notifications & Offline Sync)*

| HTTP Method | Endpoint | Mục đích cho Frontend | Request Body / Query Params | Response Data chính |
|---|---|---|---|---|
| `GET` | `/patients/{patient_id}/schedules` | Lấy toàn bộ lịch uống thuốc để Mobile tạo **Local Notification** | Path: `patient_id` | Danh sách giờ uống, ngày trong tuần, trạng thái bật nhắc |
| `POST` | `/user-medications/{id}/schedules` | Tạo lịch giờ uống cho một loại thuốc | `{ gio_uong: "08:00", ngay_trong_tuan: "2,3,4,5,6,7,CN", bat_tat_nhac: true }` | Lịch uống tạo mới |
| `PATCH` | `/schedules/{id}` | Sửa giờ uống hoặc bật/tắt nhắc nhở | `{ gio_uong?, bat_tat_nhac? }` | Lịch uống cập nhật |
| `POST` | `/dose-logs/batch-sync` | **Đồng bộ liều uống từ Mobile (hỗ trợ offline)**. Chống trùng bằng `client_uuid` | `{ logs: [ { client_uuid, medication_schedule_id, thoi_gian_du_kien, thoi_gian_thuc_uong, trang_thai } ] }` | `{ synced_count: number, duplicate_count: number }` |
| `GET` | `/patients/{patient_id}/dose-logs` | Lịch sử uống thuốc (phục vụ biểu đồ tuân thủ) | Query: `from_date`, `to_date`, `limit` | Danh sách liều đã uống/trễ/bỏ lỡ |
| `GET` | `/patients/{patient_id}/adherence-summary` | Thống kê tỷ lệ tuân thủ điều trị (7 ngày / 30 ngày) | Query: `period` (`7d` \| `30d`) | `% tuân thủ, số liều đúng giờ, số liều bỏ lỡ` |

---

### 6. Nhóm An toàn Dược lý & Cảnh báo Tương tác (Drug Safety & Interactions)
*Áp dụng: 📱 Mobile Flutter (FR04, QA.04 - Rule-based, 100% Deterministic)*

| HTTP Method | Endpoint | Mục đích cho Frontend | Request Body / Query Params | Response Data chính |
|---|---|---|---|---|
| `POST` | `/patients/{patient_id}/regimens/analyze` | Kích hoạt bộ kiểm tra an toàn trên phác đồ thuốc đang dùng | Path: `patient_id` | Tạo mới `regimen_analysis_snapshots` |
| `GET` | `/patients/{patient_id}/regimens/findings` | Lấy danh sách cảnh báo tương tác mới nhất (kèm mức độ 1-4 & chỉ dẫn) | Path: `patient_id` | Danh sách cảnh báo: Tương tác thuốc (Bảng C), Thuốc-Thực phẩm (Bảng D), Thuốc-Bệnh nền (Bảng E), kèm Disclaimers y khoa |
| `POST` | `/interactions/quick-check` | Kiểm tra nhanh trước khi kê đơn (Preview) giữa danh sách thuốc dự kiến | `{ medication_ids: [1, 2], condition_ids: [3] }` | Danh sách tương tác tức thì (không lưu DB) |
| `PATCH` | `/recommendations/{id}/acknowledge` | Đánh dấu bệnh nhân đã xem/xử lý cảnh báo | `{ da_xem: true, da_xu_ly: true }` | Cập nhật thành công |

---

### 7. Nhóm Người thân & Cảnh báo Bỏ lỡ Liều (Family Caregiver Linking)
*Áp dụng: 📱 Mobile Flutter (FR07, QA.01, QA.02)*

| HTTP Method | Endpoint | Mục đích cho Frontend | Request Body / Query Params | Response Data chính |
|---|---|---|---|---|
| `POST` | `/caregivers/link-codes` | Bệnh nhân sinh mã QR / mã 6 số để mời người thân (hạn 15 phút) | — | `{ ma: "DT-8492", het_han_luc: "..." }` |
| `POST` | `/caregivers/link-codes/redeem` | Người thân nhập mã liên kết để kết nối với bệnh nhân | `{ ma: "DT-8492" }` | Thông tin bệnh nhân đã kết nối |
| `GET` | `/caregivers/my-caregivers` | Bệnh nhân xem danh sách người thân đang liên kết | — | Danh sách người thân, trạng thái, công tắc `cho_phep_chia_se` |
| `PATCH` | `/caregivers/{link_id}` | Bệnh nhân bật/tắt chia sẻ dữ liệu hoặc thu hồi liên kết | `{ cho_phep_chia_se?: boolean, trang_thai?: 'revoked' }` | Trạng thái link cập nhật |
| `GET` | `/caregivers/monitored-patients` | Người thân lấy danh sách bệnh nhân mình đang giám sát (phục vụ Multi-Patient Switcher) | — | Danh sách bệnh nhân kèm chỉ số tuân thủ nhanh hôm nay |
| `GET` | `/notifications` | Lấy danh sách thông báo của tài khoản (nhắc nhở, cảnh báo người thân bỏ liều) | Query: `limit`, `da_doc` | Danh sách thông báo |
| `PATCH` | `/notifications/{id}/read` | Đánh dấu đã đọc thông báo | Path: `id` | Cập nhật thành công |

---

### 8. Nhóm Gợi ý Bữa ăn Phù hợp (AI Meal Suggestions)
*Áp dụng: 📱 Mobile Flutter (FR05, DPIA-controlled)*

| HTTP Method | Endpoint | Mục đích cho Frontend | Request Body / Query Params | Response Data chính |
|---|---|---|---|---|
| `POST` | `/patients/{patient_id}/meal-suggestions/generate` | Sinh gợi ý món ăn dinh dưỡng (Chỉ gửi bệnh nền và tương tác thực phẩm cần tránh qua LLM) | Path: `patient_id` | Gợi ý món ăn kèm giải thích y khoa |
| `GET` | `/patients/{patient_id}/meal-suggestions` | Lấy lịch sử các bữa ăn đã được gợi ý | Path: `patient_id` | Danh sách các gợi ý trước đó |

---

### 9. Nhóm Quản trị Danh mục & Vận hành Tuân thủ (Admin Portal)
*Áp dụng: 💻 Admin Web Next.js (FR08, FR09, QA.09, QA.10)*

| HTTP Method | Endpoint | Mục đích cho Admin Web | Request Body / Query Params |
|---|---|---|---|
| `GET/POST/PUT/DELETE` | `/admin/medications` | Quản lý danh mục thuốc thương phẩm quốc gia | CRUD Payload |
| `GET/POST/PUT/DELETE` | `/admin/active-ingredients` | Quản lý hoạt chất chuẩn hóa (Bảng A) & nhóm bệnh | CRUD Payload |
| `GET/POST/PUT/DELETE` | `/admin/conditions` | Quản lý điều kiện bệnh lý nền (Bảng B) | CRUD Payload |
| `GET/POST/PUT/DELETE` | `/admin/interactions` | Quản lý cặp tương tác thuốc (Bảng C) & ngưỡng liều | CRUD Payload |
| `GET/POST/PUT/DELETE` | `/admin/drug-foods` | Quản lý tương tác thuốc - thực phẩm (Bảng D) | CRUD Payload |
| `POST` | `/admin/catalog/sync` | Kích hoạt worker chạy ETL lấy dữ liệu Dược thư Quốc gia | — |
| `GET` | `/admin/catalog/sync-status` | Xem tiến độ job sync nền | — |
| `GET` | `/admin/unmatched-scans` | Xem danh sách chuỗi OCR chưa khớp danh mục | Query: `admin_da_xem_xet` |
| `PATCH` | `/admin/unmatched-scans/{id}/resolve` | Đánh dấu đã ánh xạ hoặc bổ sung catalog | `{ admin_da_xem_xet: true }` |
| `GET` | `/admin/audit-logs` | **Tra cứu nhật ký truy cập nhạy cảm (access_logs)** (NFR06, QA.09) | Query: `patient_id`, `actor_role`, `from`, `to` |
| `GET` | `/admin/data-deletion-requests` | Danh sách yêu cầu xóa dữ liệu chờ xử lý | Query: `trang_thai` |
| `POST` | `/admin/data-deletion-requests/{id}/process` | Phê duyệt hoặc từ chối yêu cầu xóa dữ liệu | `{ action: 'approve' \| 'reject', ly_do?: string }` |
| `GET/POST/PATCH` | `/admin/dpia-records` | Quản lý hồ sơ đánh giá rủi ro riêng tư (DPIA) | CRUD DPIA Payload |

---

## 🗺️ Lộ trình Triển khai Theo Sprint (Sprint Mapping Checklist)

```markdown
- [ ] Sprint 1 (Platform & Core Data):
  - [ ] POST /auth/sync-profile
  - [ ] GET /users/me, PATCH /users/me
  - [ ] GET /consents/me, POST /consents
  - [ ] Dependency kiểm tra quyền & Audit log base

- [ ] Sprint 2 (Core Reminders & Catalog CRUD):
  - [ ] GET /medications/search, GET /medications/{id}
  - [ ] Prescriptions & User Medications endpoints
  - [ ] Schedules endpoints & POST /dose-logs/batch-sync (idempotent)
  - [ ] Admin CRUD Catalog cơ bản

- [ ] Sprint 3 (Adherence & Family):
  - [ ] POST /caregivers/link-codes & /redeem
  - [ ] GET /caregivers/my-caregivers, /monitored-patients
  - [ ] GET /patients/{id}/adherence-summary & dose-logs
  - [ ] Background Worker push FCM cảnh báo người thân

- [ ] Sprint 4 (Medical Safety - Rule Engine):
  - [ ] Engine kiểm tra tương tác thuần túy (Thuốc-Thuốc, Thuốc-Thực phẩm, Thuốc-Bệnh)
  - [ ] POST /patients/{id}/regimens/analyze & GET /findings
  - [ ] POST /interactions/quick-check

- [ ] Sprint 5 (OCR Blister & Compliance Operations):
  - [ ] POST /medications/unmatched-scans & Admin review endpoints
  - [ ] POST & GET /data-deletion-requests (FR09)
  - [ ] GET /admin/audit-logs (NFR06)
  - [ ] Mobile Simple Mode API validation

- [ ] Sprint 6 (AI Meal & Polish):
  - [ ] POST /patients/{id}/meal-suggestions/generate (DPIA bounded)
  - [ ] Hoàn thiện bảo mật, load test 2s (NFR04).
```
