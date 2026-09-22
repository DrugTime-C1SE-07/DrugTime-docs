# DrugTime — Đặc Tả Thiết Kế API Toàn Diện (API_DESIGN.md)

> **Tiêu chuẩn:** RESTful, Contract-First, OpenAPI 3.1  
> **Backend Framework:** FastAPI (Python 3.11+)  
> **Frontend Consumers:** Flutter Mobile App (Bệnh nhân & Người thân) và Next.js 14 Admin Web (Quản trị viên)  
> **Tuân thủ quy chuẩn:** Nghị định 356/2025/NĐ-CP, Quy chuẩn bảo mật y tế NFR01–NFR07, Schema v2.  
> **Phiên bản:** v2.3 FINAL (Implementation Ready — Chốt toàn diện RBAC, Admin Override, Giám sát Kép & Four-Eyes Post-Review)

---

## 1. Kiến Trúc & Chuẩn Quy Giao Tiếp Toàn Cục

### 1.1. Base URL & Quy ước
- **Production Base URL:** `https://api.drugtime.vn/api/v1`
- **Local Dev Base URL:** `http://localhost:8000/api/v1`
- **Naming:** Đường dẫn dùng `kebab-case`, danh từ số nhiều (ví dụ: `/patients/{patient_id}/prescriptions`).
- **HTTP Methods:**
  - `GET`: Lấy dữ liệu (Idempotent, Safe).
  - `POST`: Tạo mới tài nguyên hoặc kích hoạt tác vụ.
  - `PATCH`: Cập nhật từng phần (Partial Update).
  - `DELETE`: Xóa tài nguyên (chuẩn hóa toàn bộ thành **Soft Delete** cập nhật trạng thái `archived`, chỉ nhận `Path: id`, không nhận body).

### 1.2. Envelope Chuẩn & Mã Lỗi
Mọi response đều được đóng gói theo định dạng nhất quán:

```json
// Phản hồi thành công (200 OK, 201 Created, 202 Accepted):
{
  "success": true,
  "data": { ... },
  "message": "Thông điệp phản hồi thân thiện (nếu có)"
}

// Phản hồi thất bại (400, 401, 403, 404, 409, 422, 429, 500):
{
  "success": false,
  "data": null,
  "error": {
    "code": "MA_LOI_HE_THONG",
    "message": "Mô tả lỗi tiếng Việt rõ ràng cho người dùng",
    "details": [
      { "field": "so_luong_moi_lan", "issue": "Phải lớn hơn 0" }
    ]
  }
}
```

### 1.3. Chuẩn Phân Trang (Pagination Envelope)
Áp dụng cho mọi endpoint danh sách lớn (bao gồm `/admin/audit-logs`, `/admin/rule-change-logs`, `/admin/medications`...):
```json
{
  "items": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 154,
    "total_pages": 8
  }
}
```

### 1.4. Phân Quyền Theo Ngữ Cảnh, Header `X-Admin-Reason` & Kiến Trúc Giám Sát Kép (Dual Supervision)

Hệ thống phân biệt rõ các cấp độ quyền truy cập dựa trên mối quan hệ giữa người gọi (`caller`) và bệnh nhân (`patient_id`):

1. **`self`:** Bệnh nhân tự quản lý dữ liệu cá nhân. Toàn quyền `read` và `write` nếu consent `health_data` còn hiệu lực.
2. **`family (read)`:** Người thân có liên kết `caregiver_links` trạng thái `active`, cờ `cho_phep_chia_se == true`, và bệnh nhân có consent `family_sharing`. Được phép xem đơn thuốc, lịch uống, lịch sử tuân thủ, kích hoạt phân tích an toàn, và quét thử OCR preview (không ghi DB).
3. **`family (write)`:** Người thân được bệnh nhân chủ động bật thêm cờ `cho_phep_chinh_sua == true`. Được phép kê đơn hộ, sửa giờ uống hộ người cao tuổi. Nếu cờ này bằng `false`, mọi thao tác ghi bị chặn `403 INSUFFICIENT_WRITE_PERMISSION`.
4. **Header dùng chung `X-Admin-Reason`:**
   - Quản trị viên hệ thống **không** được cấp quyền `write` tự do trên hồ sơ bệnh án của bệnh nhân.
   - Lý do can thiệp của Admin được truyền tập trung qua HTTP Header: **`X-Admin-Reason: <string>`**.
   - **Quy tắc kiểm tra tập trung:** Khi `actor_role == 'admin'` thực hiện thao tác can thiệp dữ liệu bệnh nhân (`admin_override`), dependency `verify_patient_access` kiểm tra header:
     - Header bắt buộc phải có mặt và độ dài chuỗi tối thiểu **10 ký tự**.
     - Nếu thiếu hoặc < 10 ký tự → Hệ thống từ chối ngay với HTTP **`422 ADMIN_OVERRIDE_REASON_REQUIRED`**.
   - `access_logs` tự động trích xuất nội dung từ header để lưu vào `ly_do_can_thiep`.

#### 1.4.1. Kiến Trúc Giám Sát Kép (Dual Supervision Architecture)
Phase 1 phân tách rành mạch mức độ giám sát giữa 2 loại can thiệp của Admin để vừa đảm bảo an toàn vừa tối ưu vận hành:

| Loại can thiệp | Header `X-Admin-Reason` | Audit Log | Tự Động Re-Analysis | Four-Eyes Hậu Kiểm |
|---|:---:|:---:|:---:|:---:|
| **Caregiver Emergency Override** (`PATCH /caregivers/{link_id}`) | Bắt buộc | Có | Không áp dụng | **Có (≤ 24h)** |
| **Clinical Admin Override** (`conditions`, `prescriptions`, `schedules`) | Bắt buộc | Có | **Có (Snapshot & Findings)** | Không (Phase 1) |
| **Admin Catalog/Rule Change** (`admin/interactions`, `admin/drug-foods`) | Theo chính sách | Có (`rule_catalog`) | Không | Không |
| **Admin Audit Post-Review** (`admin/audit-logs/{id}/post-review`) | Không | Có | Không | **Bắt buộc Admin khác** |

- **Clinical Admin Override:** Luôn được bảo vệ bởi cơ chế kiểm tra an toàn tự động (`Automatic Regimen Analysis`). Mọi can thiệp y tế đều kích hoạt snapshot phân tích tương tác tức thì và cập nhật findings, do đó không cần Four-Eyes trong Phase 1.
- **Caregiver Emergency Override:** Có tính chất can thiệp khẩn cấp (thu hồi quyền người thân để bảo vệ người cao tuổi bị lạm dụng hoặc mất kiểm soát thiết bị). Hành vi này không có cơ chế phân tích tự động nào kiểm tra lại, do đó **bắt buộc áp dụng Four-Eyes Post-Review trong 24h**.

### 1.5. Chi Tiết Cơ Chế Four-Eyes Post-Action Review (Hậu Kiểm trong 24 Giờ)

Áp dụng cho các thao tác can thiệp khẩn cấp (`is_emergency_override = true`) trên `PATCH /caregivers/{link_id}`:

```text
Emergency Action (Admin A + X-Admin-Reason)
       ↓
Immediate Protection (Link Revoked)
       ↓
Audit Event #1 (is_emergency_override = true, review_status = 'pending_post_review')
       ↓
Automatic In-App Notification sent to Patient
       ↓
Review Deadline = created_at + 24h (Server-calculated)
       ↓
Post-Review (Admin B, B != A, POST /admin/audit-logs/{id}/post-review)
       ↓
Audit Event #2 (decision: valid | invalid, review_note: 10-2000 chars)
       ├── decision = 'valid'   → review_status = 'reviewed_valid'
       └── decision = 'invalid' → review_status = 'reviewed_invalid'
                                  + Flag 'COMPLIANCE_REVIEW_REQUIRED'
                                  + Notification to Compliance Team
                                  (KHÔNG tự động khôi phục quyền caregiver)
```

#### Các Ràng Buộc Kiểm Tra Hậu Kiểm Bắt Buộc (5 Guardrails):
Admin thực hiện hậu kiểm phải thỏa mãn toàn bộ điều kiện:
1. Phải có vai trò Quản trị viên (`actor_role == admin`). Vi phạm trả `403 INSUFFICIENT_ADMIN_PERMISSION`.
2. **Chống tự hậu kiểm:** Quản trị viên không được tự hậu kiểm hành động của chính mình (`reviewer_user_id != audit_log.actor_user_id`). Vi phạm trả **`403 CANNOT_REVIEW_OWN_ACTION`**.
3. Bản ghi phải là thao tác can thiệp khẩn cấp (`audit_log.is_emergency_override == true`). Vi phạm trả `409 REVIEW_NOT_REQUIRED`.
4. Bản ghi chưa từng được hậu kiểm (`audit_log.review_status == 'pending_post_review'`). Vi phạm trả `409 REVIEW_ALREADY_COMPLETED`.
5. Thời điểm hậu kiểm phải nằm trong thời hạn 24h (`now <= audit_log.review_deadline`). Quá hạn trả `409 POST_REVIEW_DEADLINE_EXCEEDED`. (Hệ thống worker định kỳ quét các bản ghi quá hạn để gắn cờ `POST_REVIEW_OVERDUE`).

---

## 1.6. Ma Trận Phân Quyền Cuối Cùng (Final RBAC Matrix)

| Hành động (Operation) | Self (Bệnh nhân) | Family Read (Người thân xem) | Family Write (Người thân ghi) | Admin (Quản trị viên) |
|---|:---:|:---:|:---:|:---:|
| **Xem hồ sơ y tế bệnh nhân** | ✅ | ✅ | ✅ | ✅ *(Theo chính sách audit)* |
| **Tạo / Sửa đơn thuốc** | ✅ | ❌ | ✅ | ⚠️ `admin_override` + `X-Admin-Reason` |
| **Sửa liều lượng thuốc** | ✅ | ❌ | ✅ | ⚠️ `admin_override` + `X-Admin-Reason` |
| **Tạo / Sửa lịch giờ uống** | ✅ | ❌ | ✅ | ⚠️ `admin_override` + `X-Admin-Reason` |
| **Xóa mềm dữ liệu lâm sàng** | ✅ | ❌ | ✅ | ⚠️ `admin_override` + `X-Admin-Reason` |
| **Quét OCR xem trước (preview)** | ✅ | ✅ | ✅ | ✅ |
| **Kích hoạt phân tích tương tác phác đồ** | ✅ | ✅ | ✅ | ✅ |
| **Xác nhận đã đọc khuyến nghị an toàn** | ✅ | ❌ | ❌ | ❌ *(Chỉ bệnh nhân tự quyết)* |
| **Thu hồi liên kết Caregiver** | ✅ | ❌ | ❌ | ⚠️ `admin_override` + Four-Eyes ≤ 24h |
| **Cấp thêm quyền cho Caregiver** | ✅ | ❌ | ❌ | ❌ *(Cấm tuyệt đối Admin)* |
| **Hậu kiểm thao tác khẩn cấp** | ❌ | ❌ | ❌ | ✅ *(Bắt buộc Admin khác)* |

---

## 2. Chi Tiết Toàn Bộ Endpoints Theo 9 Nhóm Chức Năng

### Nhóm 1: Xác Thực & Người Dùng (Auth & User Profile)
*Tags:* `1. Auth & User Profile`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `POST` | `/auth/sync-profile` | Đồng bộ hồ sơ từ Supabase Auth sang Postgres khi user đăng ký/đăng nhập | `SyncProfileRequest` | `UserResponse` | 200 OK | Authenticated | Không |
| `GET` | `/users/me` | Lấy thông tin user hiện tại, trạng thái Simple Mode | — | `UserResponse` | 200 OK | `self` | Không |
| `PATCH` | `/users/me` | Cập nhật hồ sơ cá nhân, bật/tắt `che_do_nguoi_cao_tuoi` | `UpdateProfileRequest` | `UserResponse` | 200 OK | `self` | Không |
| `POST` | `/users/me/data-export` | **Khởi tạo job xuất bản sao dữ liệu cá nhân bất đồng bộ (NĐ 356)** | `DataExportJobCreate` | `DataExportJobResponse` | 202 Accepted | `self` | Có (`ho_so_suc_khoe`) |
| `GET` | `/users/me/data-export/jobs/{job_id}` | **Poll tiến độ & lấy link tải file ZIP/JSON bản sao dữ liệu (hạn 24h)** | Path: `job_id` | `DataExportJobStatusResponse` | 200 OK | `self` | Có (`ho_so_suc_khoe`) |
| `POST` | `/users/me/device-tokens` | Đăng ký FCM Device Token nhận cảnh báo liều | `DeviceTokenRequest` | `MessageResponse` | 201 Created | `self` | Không |
| `DELETE`| `/users/me/device-tokens/{fcm_token}` | Hủy đăng ký token khi đăng xuất | — | `MessageResponse` | 200 OK | `self` | Không |

---

### Nhóm 2: Đồng Thuận Dữ Liệu & Quyền Riêng Tư (Consent & Privacy - NĐ 356)
*Tags:* `2. Consent & Privacy`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `GET` | `/consents/me` | Danh sách trạng thái đồng thuận từng mục đích (`health_data`, `family_sharing`, `ai_meal`) | — | `List[ConsentStatusResponse]` | 200 OK | `self` | Có (`ho_so_suc_khoe`) |
| `POST` | `/consents` | Cấp mới hoặc thu hồi đồng thuận (Append-only lưu lịch sử) | `SubmitConsentRequest` | `ConsentRecordResponse` | 201 Created | `self` | Có (`ho_so_suc_khoe`) |
| `POST` | `/data-deletion-requests` | Gửi yêu cầu xóa toàn bộ dữ liệu hoặc rút consent (FR09) | `DataDeletionRequestCreate` | `DataDeletionRequestResponse` | 202 Accepted | `self` | Có (`ho_so_suc_khoe`) |
| `GET` | `/data-deletion-requests/me` | Xem tiến độ các yêu cầu xóa dữ liệu của mình | — | `List[DataDeletionRequestResponse]` | 200 OK | `self` | Không |

---

### Nhóm 3: Hồ Sơ Sức Khỏe & Bệnh Lý Nền (Conditions)
*Tags:* `3. Medical Conditions`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `GET` | `/conditions` | Tra cứu danh mục bệnh chuẩn hóa (Bảng B - tiểu đường, suy thận...) | Query: `q`, `limit` | `List[ConditionCatalogResponse]` | 200 OK | Authenticated | Không |
| `GET` | `/patients/{patient_id}/conditions` | Lấy danh sách bệnh nền của bệnh nhân (kèm phân độ/subtype) | Path: `patient_id` | `List[UserConditionResponse]` | 200 OK | `read` (`self`/`family`/`admin`) | Có (`ho_so_suc_khoe`) |
| `POST` | `/patients/{patient_id}/conditions` | Thêm bệnh lý nền. **Tự động kích hoạt kiểm tra tương tác** | `UserConditionCreate` | `UserConditionResponse` | 201 Created | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`ho_so_suc_khoe`) |
| `DELETE`| `/patients/{patient_id}/conditions/{id}` | **Soft-delete** bệnh nền (đổi `trang_thai: archived`). **Tự động re-analyze** | Path: `id` | `MessageResponse` | 200 OK | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`ho_so_suc_khoe`) |

---

### Nhóm 4: Đơn Thuốc & Danh Mục Thuốc (Prescriptions & Medications)
*Tags:* `4. Prescriptions & Medications`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `GET` | `/medications/search` | Tra cứu danh mục thuốc quốc gia (theo tên, hoạt chất) | Query: `q`, `limit` | `List[MedicationCatalogResponse]` | 200 OK | Authenticated | Không |
| `GET` | `/medications/{id}` | Chi tiết thuốc chuẩn hóa & hoạt chất Bảng A | Path: `id` | `MedicationDetailResponse` | 200 OK | Authenticated | Không |
| `POST` | `/medications/unmatched-scans` | Ghi nhận chuỗi quét OCR không khớp catalog (R-01) để Admin duyệt | `UnmatchedScanCreate` | `UnmatchedScanResponse` | 201 Created | Authenticated | Không |
| `POST` | `/patients/{patient_id}/prescriptions/ocr-upload` | **Upload ảnh/PDF vỉ thuốc nhận diện OCR preview (Max 10MB; JPG, PNG, WEBP, PDF; Không ghi rác DB). Quyền READ.** | Multipart: `file: UploadFile` | `OcrUploadResponse` | 200 OK | **`read` (`self`/`family`/`admin`)** | Có (`danh_sach_thuoc`) |
| `GET` | `/patients/{patient_id}/prescriptions` | Danh sách đơn thuốc (lọc theo `trang_thai: dang_dung \| da_ket_thuc`) | Query: `trang_thai` | `List[PrescriptionResponse]` | 200 OK | `read` (`self`/`family`/`admin`) | Có (`danh_sach_thuoc`) |
| `POST` | `/patients/{patient_id}/prescriptions` | Tạo đơn thuốc mới kèm danh sách thuốc. **Tự động re-analyze** | `PrescriptionCreate` | `PrescriptionResponse` | 201 Created | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`danh_sach_thuoc`) |
| `GET` | `/prescriptions/{id}` | Chi tiết 1 đơn thuốc và các thuốc con | Path: `id` | `PrescriptionResponse` | 200 OK | `read` (`self`/`family`/`admin`) | Có (`danh_sach_thuoc`) |
| `PATCH` | `/prescriptions/{id}` | Sửa metadata đơn thuốc (`ngay_ke_don`, `noi_ke_don`) sau khi OCR quét sai | `PrescriptionUpdateMetadata` | `PrescriptionResponse` | 200 OK | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`danh_sach_thuoc`) |
| `PATCH` | `/prescriptions/{id}/status` | Kết thúc đơn thuốc (`trang_thai: da_ket_thuc`). **Tự động re-analyze** | `PrescriptionUpdateStatus` | `PrescriptionResponse` | 200 OK | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`danh_sach_thuoc`) |
| `POST` | `/prescriptions/{id}/medications` | Thêm thuốc lẻ vào đơn thuốc. **Tự động re-analyze** | `UserMedicationCreate` | `UserMedicationResponse` | 201 Created | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`danh_sach_thuoc`) |
| `PATCH` | `/user-medications/{id}` | Sửa liều lượng (`so_luong_moi_lan`, `so_lan_moi_ngay`). **Tự động re-analyze** | `UserMedicationUpdate` | `UserMedicationResponse` | 200 OK | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`danh_sach_thuoc`) |
| `DELETE`| `/user-medications/{id}` | **Soft-delete** thuốc (`trang_thai: archived`). **Tự động re-analyze** | Path: `id` | `MessageResponse` | 200 OK | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`danh_sach_thuoc`) |

---

### Nhóm 5: Lịch Uống & Ghi Nhận Liều (Schedules & Dose Logging)
*Tags:* `5. Schedules & Dose Logs`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `GET` | `/patients/{patient_id}/schedules` | Lấy danh sách lịch giờ uống để Mobile thiết lập **Local Notification** | Path: `patient_id` | `List[ScheduleResponse]` | 200 OK | `read` (`self`/`family`/`admin`) | Có (`lich_su_tuan_thu`) |
| `POST` | `/user-medications/{id}/schedules` | Tạo lịch uống (`loai_lich: co_dinh \| khi_can`, `gio_uong`, `ngay_trong_tuan`) | `ScheduleCreate` | `ScheduleResponse` | 201 Created | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`lich_su_tuan_thu`) |
| `PATCH` | `/schedules/{id}` | Sửa giờ uống, bật/tắt thông báo nhắc | `ScheduleUpdate` | `ScheduleResponse` | 200 OK | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`lich_su_tuan_thu`) |
| `DELETE`| `/schedules/{id}` | **Soft-delete** lịch uống thuốc (`trang_thai: archived`) | Path: `id` | `MessageResponse` | 200 OK | `write` (`self`/`family`) \| `admin_override` *(bắt buộc header `X-Admin-Reason`)* | Có (`lich_su_tuan_thu`) |
| `POST` | `/dose-logs/batch-sync` | **Đồng bộ liều uống từ client offline (chống trùng lặp bằng `client_uuid`, trả kết quả per-item)** | `BatchDoseLogSyncRequest` | `BatchDoseLogSyncResponse` | 200 OK | `self` | Có (`lich_su_tuan_thu`) |
| `GET` | `/patients/{patient_id}/dose-logs` | Lấy lịch sử uống thuốc (`from`, `to`, phân trang) | Query: `from_date`, `to_date`, `page`, `page_size` | `PaginatedDoseLogsResponse` | 200 OK | `read` (`self`/`family`/`admin`) | Có (`lich_su_tuan_thu`) |
| `GET` | `/patients/{patient_id}/adherence-summary` | Tỷ lệ tuân thủ điều trị (đúng giờ, trễ, bỏ lỡ trong 7 hoặc 30 ngày) | Query: `period` (`7d` \| `30d`) | `AdherenceSummaryResponse` | 200 OK | `read` (`self`/`family`/`admin`) | Có (`lich_su_tuan_thu`) |

---

### Nhóm 6: An Toàn Dược Lý & Cảnh Báo Tương Tác (Drug Safety & Interactions)
*Tags:* `6. Drug Safety & Interactions`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `POST` | `/patients/{patient_id}/regimens/analyze` | Kích hoạt bộ kiểm tra an toàn toàn diện (Thuốc-Thuốc, Thuốc-Thực phẩm, Thuốc-Bệnh nền). **Hàm thuần tạo snapshot, không đổi dữ liệu gốc.** | Path: `patient_id` | `RegimenSnapshotResponse` | 200 OK | **`read`** (`self`/`family`/`admin`) | Có (`canh_bao_tuong_tac`) |
| `GET` | `/patients/{patient_id}/regimens/findings` | Lấy danh sách phát hiện tương tác mới nhất (mức độ 1-4, chỉ dẫn y khoa, disclaimers) | Path: `patient_id` | `List[RegimenFindingResponse]` | 200 OK | `read` (`self`/`family`/`admin`) | Có (`canh_bao_tuong_tac`) |
| `POST` | `/interactions/quick-check` | Kiểm tra nhanh tương tác tức thì trước khi kê đơn (Preview không lưu DB) | `QuickCheckRequest` | `QuickCheckResponse` | 200 OK | Authenticated | Không |
| `PATCH` | `/recommendations/{id}/acknowledge` | **Đánh dấu bệnh nhân đã xem/đã xử lý khuyến nghị. (Chỉ `self`, không ủy quyền cho family/admin vì trách nhiệm pháp lý)** | `AcknowledgeRecommendationRequest` | `MessageResponse` | 200 OK | **`self` (duy nhất)** | Có (`canh_bao_tuong_tac`) |

---

### Nhóm 7: Người Thân & Cảnh Báo Bỏ Lỡ Liều (Caregivers & Missed Dose)
*Tags:* `7. Caregiver & Family Linking`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `POST` | `/caregivers/link-codes` | **Bệnh nhân sinh mã 6 số / QR mời người thân (hạn 15 phút, Multi-use trong 15p cho nhiều con cùng kết nối; tự động hủy các mã active trước đó của bệnh nhân)** | — | `LinkCodeResponse` | 201 Created | `self` | Không |
| `POST` | `/caregivers/link-codes/redeem` | **Người thân nhập mã liên kết. (Multi-use trong 15p; Rate-limit kép: 5 lần sai/15p theo caller + Tự vô hiệu hóa mã nếu bị dò sai > 10 lần toàn cục)** | `RedeemLinkCodeRequest` | `CaregiverLinkResponse` | 200 OK | Authenticated *(Rate-limited)* | Không |
| `GET` | `/caregivers/my-caregivers` | Bệnh nhân xem danh sách người thân đang liên kết | — | `List[CaregiverLinkResponse]` | 200 OK | `self` | Không |
| `PATCH` | `/caregivers/{link_id}` | **Cập nhật quyền hoặc thu hồi liên kết. Bổ sung `admin_override` bảo vệ người cao tuổi (chỉ được thu hồi/thu hẹp quyền, bắt buộc header `X-Admin-Reason`, tự động gửi thông báo in-app cho bệnh nhân, sinh Four-Eyes deadline 24h).** | `CaregiverLinkUpdateRequest` | `CaregiverLinkResponse` | 200 OK | **`self` \| `admin_override` *(chỉ thu hồi, bắt buộc header `X-Admin-Reason`)* ** | Có (`ho_so_suc_khoe`) |
| `GET` | `/caregivers/monitored-patients` | Lấy danh sách bệnh nhân đang giám sát (phục vụ Multi-Patient Switcher) | — | `List[MonitoredPatientResponse]` | 200 OK | `family` | Có (`ho_so_suc_khoe`) |
| `GET` | `/notifications` | Lấy thông báo của user (nhắc thuốc, cảnh báo người thân bỏ liều) | Query: `page`, `page_size`, `da_doc` | `PaginatedNotificationsResponse` | 200 OK | `self` | Không |
| `PATCH` | `/notifications/{id}/read` | Đánh dấu đã đọc thông báo | Path: `id` | `MessageResponse` | 200 OK | `self` | Không |

---

### Nhóm 8: Gợi Ý Món Ăn Dinh Dưỡng (AI Meal Suggestions)
*Tags:* `8. AI Meal Suggestions`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `POST` | `/patients/{patient_id}/meal-suggestions/generate` | **Khởi tạo job sinh gợi ý món ăn bất đồng bộ (trả về `job_id`, timeout 60s)** | `MealSuggestionGenerateRequest` | `MealSuggestionJobResponse` | 202 Accepted | `self` | Có (`goi_y_bua_an`) |
| `GET` | `/patients/{patient_id}/meal-suggestions/jobs/{job_id}`| **Poll tiến độ job LLM sinh gợi ý món ăn (`pending \| processing \| completed \| failed`)** | Path: `patient_id`, `job_id` | `MealSuggestionJobStatusResponse` | 200 OK | `self`, `family` | Có (`goi_y_bua_an`) |
| `GET` | `/patients/{patient_id}/meal-suggestions` | Lịch sử các bữa ăn đã được gợi ý | Path: `patient_id` | `List[MealSuggestionResponse]` | 200 OK | `read` (`self`/`family`/`admin`) | Có (`goi_y_bua_an`) |

---

### Nhóm 9: Quản Trị Danh Mục & Vận Hành Tuân Thủ (Admin Portal)
*Tags:* `9. Admin Operations`

| Method | Path | Mô tả | Request Schema | Response Schema | HTTP Status | RBAC | Ghi Log? |
|---|---|---|---|---|---|---|---|
| `GET` | `/admin/medications` | Danh sách danh mục thuốc (phân trang, tìm kiếm) | Query: `q`, `page`, `page_size` | `PaginatedMedicationsResponse` | 200 OK | `admin` | Không |
| `POST` | `/admin/medications` | Tạo mới thuốc thương mại quốc gia | `AdminMedicationCreate` | `MedicationCatalogResponse` | 201 Created | `admin` | **Có (`rule_catalog`)** |
| `PUT` | `/admin/medications/{id}` | Cập nhật thuốc thương mại | `AdminMedicationUpdate` | `MedicationCatalogResponse` | 200 OK | `admin` | **Có (`rule_catalog`)** |
| `DELETE`| `/admin/medications/{id}` | Xóa thuốc khỏi catalog | Path: `id` | `MessageResponse` | 200 OK | `admin` | **Có (`rule_catalog`)** |
| `GET/POST/PUT/DELETE` | `/admin/active-ingredients` | Quản lý hoạt chất chuẩn hóa (Bảng A) | CRUD Request | CRUD Response | 200/201 OK | `admin` | **Có (`rule_catalog`)** |
| `GET/POST/PUT/DELETE` | `/admin/conditions` | Quản lý điều kiện bệnh lý nền (Bảng B) | CRUD Request | CRUD Response | 200/201 OK | `admin` | **Có (`rule_catalog`)** |
| `GET/POST/PUT/DELETE` | `/admin/interactions` | Quản lý cặp tương tác thuốc (Bảng C) & ngưỡng liều | CRUD Request | CRUD Response | 200/201 OK | `admin` | **Có (`rule_catalog`)** |
| `GET/POST/PUT/DELETE` | `/admin/drug-foods` | Quản lý tương tác thuốc - thực phẩm (Bảng D) | CRUD Request | CRUD Response | 200/201 OK | `admin` | **Có (`rule_catalog`)** |
| `GET` | `/admin/rule-change-logs` | **Tra cứu nhật ký thay đổi luật tương tác & catalog (Phân trang, rollback audit)** | Query: `table_name`, `changed_by`, `from_date`, `to_date`, `page`, `page_size` | `PaginatedRuleChangeLogsResponse` | 200 OK | `admin` | **Có (`rule_catalog`)** |
| `POST` | `/admin/catalog/sync` | Kích hoạt worker chạy ETL lấy dữ liệu Dược thư Quốc gia | — | `SyncTriggerResponse` | 202 Accepted | `admin` | **Có (`rule_catalog`)** |
| `GET` | `/admin/catalog/sync-status` | Xem trạng thái tiến trình sync nền | — | `SyncStatusResponse` | 200 OK | `admin` | Không |
| `GET` | `/admin/unmatched-scans` | Danh sách chuỗi OCR chưa khớp catalog (phân trang) | Query: `admin_da_xem_xet`, `page`, `page_size` | `PaginatedUnmatchedScansResponse` | 200 OK | `admin` | Không |
| `PATCH` | `/admin/unmatched-scans/{id}/resolve` | Đánh dấu đã ánh xạ hoặc thêm vào catalog | `ResolveUnmatchedScanRequest` | `MessageResponse` | 200 OK | `admin` | **Có (`rule_catalog`)** |
| `GET` | `/admin/audit-logs` | **Tra cứu nhật ký truy cập dữ liệu nhạy cảm (có phân trang NFR06, QA.09, lọc theo can thiệp khẩn cấp `is_emergency_override` và trạng thái `review_status`)** | Query: `patient_id`, `actor_role`, `from_date`, `to_date`, `page`, `page_size`, `is_emergency_override`, `review_status` | `PaginatedAuditLogsResponse` | 200 OK | `admin` | Có (`admin`) |
| `POST` | `/admin/audit-logs/{id}/post-review` | **Xác nhận hậu kiểm Four-Eyes trong 24h cho thao tác can thiệp khẩn cấp của Admin (Hỗ trợ 3 trạng thái: pending_post_review, reviewed_valid, reviewed_invalid)** | `AuditPostReviewRequest` | `AuditPostReviewResponse` | 200 OK | **`admin` (bắt buộc khác actor_user_id)** | Có (`admin`) |
| `GET` | `/admin/data-deletion-requests` | Danh sách yêu cầu xóa dữ liệu chờ duyệt | Query: `trang_thai`, `page`, `page_size` | `PaginatedDeletionRequestsResponse` | 200 OK | `admin` | Có (`admin`) |
| `POST` | `/admin/data-deletion-requests/{id}/process` | Duyệt / Từ chối yêu cầu xóa dữ liệu cá nhân (kèm lý do) | `ProcessDeletionRequest` | `MessageResponse` | 200 OK | `admin` | Có (`admin`) |
| `GET/POST/PATCH` | `/admin/dpia-records` | Quản lý hồ sơ đánh giá tác động quyền riêng tư (DPIA) | CRUD Request | CRUD Response | 200/201 OK | `admin` | Có (`admin`) |
