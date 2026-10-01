# DrugTime — Schema Cơ Sở Dữ Liệu (Bản Chốt v8)

Capstone Project 1 (C1SE.07), International School, Đại học Duy Tân.

Ký hiệu thay đổi: **[MỚI]** = bảng/cột mới, **[SỬA]** = bảng/cột đã chỉnh, **[XÓA]** = đã loại bỏ. Ký hiệu trong bảng áp dụng cho thay đổi **gần nhất tính đến v7**; các thay đổi cũ hơn giữ nguyên như tài liệu gốc và không đánh dấu lại. v8 chỉ đổi tên định danh (không đổi cấu trúc) nên không đánh dấu lại từng bảng — xem Phụ lục.

## Lịch sử thay đổi

### v2 → v3
Phát sinh từ việc rà soát Sprint Backlog đối chiếu với Schema v2 (xem `DrugTime_Sprint_Backlog_Task_Descriptions.md`, mục 0):

1. **Xóa mềm cho danh mục** — PB04/PB05 yêu cầu xóa mềm nhưng `medications`, `active_ingredient_interactions`, `drug_food_interactions` chưa có cột đánh dấu. → thêm `deleted_at` (nullable) cho cả 3 bảng.
2. **Nhật ký đồng bộ danh mục** — PB06 yêu cầu "sync log with timestamp + record count" nhưng chưa có bảng lưu. → thêm bảng `catalog_sync_runs`.
3. **Chống trùng lượt uống** — job phát hiện bỏ lỡ (PB20) và API xác nhận liều (PB13) có thể cùng ghi vào `dose_logs` cho cùng một lượt nếu chạy gần nhau. → thêm `UNIQUE(medication_schedule_id, scheduled_at)` trên `dose_logs`.
4. ~~Thuốc ngoài danh mục: thêm `free_text_name` tự do~~ — sửa ở v3 → v4, rồi **bỏ hẳn ở v4 → v5** (xem bên dưới).
5. **Simple Mode không cần lưu server** — `users.senior_mode` là tùy chọn giao diện của thiết bị đang dùng, không phải dữ liệu cần chia sẻ hay đồng bộ. → bỏ cột, chuyển sang lưu cục bộ trên máy (`SharedPreferences`/`UserDefaults`).

### v3 → v4

1. **Đăng nhập bằng email hoặc SĐT** — PB01 cho phép cả hai. → thêm `users.email` (nullable, UNIQUE), ràng buộc phải có ít nhất một trong email/SĐT.
2. ~~Thuốc ngoài danh mục — chống trùng lặp bằng bảng gom nhóm `free_text_medication_names`~~ — **bỏ hẳn ở v4 → v5**, xem bên dưới.
3. **Xác nhận không mua Apple Developer Program (trả phí)** — team dùng Apple ID miễn phí cho toàn bộ Phase 1. Không đổi cấu trúc bảng, nhưng ghi nhận hệ quả ở ghi chú §14: build iOS chỉ cài được qua Xcode trực tiếp (không TestFlight/Ad Hoc), và **FCM push không hoạt động trên iOS** vì thiếu APNs — ảnh hưởng trực tiếp tới PB20 (cảnh báo bỏ lỡ liều cho người thân dùng iOS).

### v4 → v5

1. **Bỏ hẳn việc nhập tự do cho thuốc** — quyết định mới: Admin sẽ chủ động bổ sung đủ thuốc cần dùng vào danh mục (`medications`) thay vì để patient tự gõ tên khi không khớp. → bỏ bảng `free_text_medication_names`; `user_medications.medication_id` trở lại **bắt buộc** (NOT NULL), bỏ cột `free_text_name` và `free_text_medication_id`.
2. **Kết quả tra tương tác khi thiếu dữ liệu**: giữ nguyên nguyên tắc 3 trạng thái (có tương tác / đã kiểm tra không thấy / không đủ dữ liệu). Trạng thái "không đủ dữ liệu" giờ chỉ xảy ra khi thuốc **có trong danh mục nhưng chưa được Admin gán hoạt chất** — không còn phát sinh từ việc người dùng gõ tên tự do, vì đường đó không còn tồn tại.

Không có thay đổi phá vỡ tương thích ngược ở vòng này ngoài việc siết `medication_id` về NOT NULL — cần đảm bảo dữ liệu hiện có (nếu đã có dòng NULL từ v3/v4) được gán lại trước khi migrate.

### v5 → v6

1. **Bỏ `unmatched_scan_logs` cho đơn giản** — bảng ghi lại chuỗi ML Kit không khớp danh mục bị loại bỏ. → bỏ bảng. Hệ quả: task **4.11 (Log unmatched items for Admin catalog review, PB31)** trong Sprint Backlog mất phần dữ liệu để dựa vào — Admin không còn nguồn tự động cho biết thuốc nào bị quét hụt nhiều lần để ưu tiên bổ sung; phải dựa vào phản hồi thủ công từ người dùng hoặc theo dõi qua kênh khác. R-01 (rủi ro quét không khớp) vẫn được giảm nhẹ bằng fallback tìm thủ công (3.05), chỉ mất phần "biết để bổ sung danh mục".

### v6 → v7

1. **`access_logs` không còn ghi truy cập `self`** — NFR06 và QA.09 chỉ yêu cầu log truy cập của Family Member và Admin; patient xem dữ liệu của chính mình nằm ngoài yêu cầu, và ghi mọi lần mở màn hình/xác nhận liều làm bảng phình to, thêm một lần ghi đồng bộ trên đường xác nhận liều (QA.05, NFR04). → `actor_role` đổi từ `self / family / admin` thành `family / admin / khong_co_quyen`. Nhánh `C = P` trong quy tắc phân quyền vẫn kiểm tra consent của P (QA.01) nhưng **không ghi** `access_logs`.
2. **Giá trị `khong_co_quyen`** — chỉ dùng cho dòng `result = 'denied'`, để vẫn log được người không phải family/admin (đã unlink, bị thu hồi quyền, sửa patient ID trong request — QA.02, QA.09). Thêm `CHECK (result = 'allowed' → actor_role IN ('family','admin'))`.

Hệ quả: request bị từ chối do chính patient đã rút consent (QA.01) không để lại dòng log. Migrate: xóa các dòng `actor_role = 'self'` (nếu có) trước khi đổi ENUM.

### v7 → v8 (bản này)

1. **Tên bảng và tên cột chuyển toàn bộ sang tiếng Anh** (snake_case). Các phần còn lại giữ tiếng Việt: mô tả, ghi chú, và **giá trị ENUM** (vd `dong_y`, `cho_duyet`, `chong_chi_dinh`, `Đã uống`) — giá trị ENUM là dữ liệu, không phải tên định danh, nên không đổi.
2. **Chỉ đổi tên, không đổi cấu trúc, kiểu dữ liệu hay ràng buộc.** Bảng đối chiếu đầy đủ tên cũ → tên mới ở Phụ lục cuối tài liệu. Các tên nhắc trong lịch sử thay đổi (v2 → v7) đã được cập nhật theo tên mới để tài liệu nhất quán.
3. Bảng đổi tên: `don_thuoc` → `prescriptions`, `active_ingredient_nhom_benh` → `active_ingredient_disease_groups`, `kich_ban_benh_nhan_mau` → `sample_patient_scenarios`, `kich_ban_dieu_kien` → `scenario_conditions`, `kich_ban_hoat_chat` → `scenario_active_ingredients`. Các bảng còn lại vốn đã có tên tiếng Anh.
4. `access_logs.ly_do_tu_choi` và `data_deletion_requests.ly_do_tu_choi` cùng đổi thành `rejection_reason` (cùng nghĩa, giữ đặt tên nhất quán).
5. Migrate: dùng `ALTER TABLE ... RENAME TO` / `RENAME COLUMN` (đổi tên không mất dữ liệu). Cần cập nhật đồng thời code Backend/Worker, RLS, index, constraint, seed/ETL script và các tài liệu tham chiếu tên cũ (`drugtime_mobile_backend_components.md`, Sprint Backlog).

---

## Nhóm 1 — Danh mục thuốc

### `medications` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `name` | |
| `raw_active_ingredient` | Text thô từ nguồn dữ liệu gốc, dùng để đối chiếu khi mapping |
| `strength_text` | Text gốc, dùng để hiển thị |
| `dosage_form` | |
| `manufacturer_name` | |
| `manufacturer_country` | |
| `packaging_spec` | |
| `deleted_at` | **[MỚI]** nullable — xóa mềm; NULL = đang lưu hành trong ứng dụng |

> Mọi truy vấn của Mobile/Admin (trừ màn quản trị "xem đã xóa") phải lọc `deleted_at IS NULL`. Bản ghi có `deleted_at` khác NULL vẫn được `medication_active_ingredients`, `user_medications` tham chiếu để giữ lịch sử — không xóa cứng khi còn tham chiếu.

### `active_ingredients` (Bảng A)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `standard_name` | |
| `role` | ENUM: `dieu_tri_benh_nen` / `trieu_chung_cap_tinh` |
| `disease_group` | FK nullable |
| `pharmacological_group` | |
| `atc_code` | |
| `source` | |

### `ingredient_aliases`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK → `active_ingredients.id` |
| `alias_text` | Tên gọi khác (thương mại, viết tắt, tiếng Anh/Việt...) |

---

## Nhóm 2 — Lớp nối ETL

### `medication_active_ingredients`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `medication_id` | FK → `medications.id` |
| `active_ingredient_id` | FK → `active_ingredients.id` |
| `strength_value` | Số, vd `500` |
| `strength_unit` | vd `"mg"`, `"mcg"`, `"mg/5ml"` |
| `dosing_unit` | vd `"viên"`, `"ml"`, `"gói"` |

Cho phép 1 thuốc có nhiều hoạt chất (thuốc phối hợp) với hàm lượng có cấu trúc, phục vụ tính tổng liều/ngày.

### `active_ingredient_disease_groups`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK |
| `disease_group` | ENUM |

### `catalog_sync_runs` **[MỚI]**
Phục vụ PB06 (nhật ký đồng bộ danh mục từ Nguồn dữ liệu quản lý dược Việt Nam).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `source` | ENUM: `dav_drugbank` / `qd_5948` / `duoc_thu_qg` — nguồn nào được đồng bộ |
| `started_at` | |
| `finished_at` | nullable — NULL nếu job đang chạy hoặc bị treo |
| `status` | ENUM: `dang_chay` / `thanh_cong` / `that_bai` |
| `records_inserted` | mặc định 0 |
| `records_updated` | mặc định 0 |
| `records_failed` | mặc định 0 |
| `error_details` | nullable — text/JSON tóm tắt các bản ghi lỗi (không lưu toàn bộ payload) |
| `triggered_by` | ENUM: `scheduler` / `admin_thu_cong` |

> Index: `(source, started_at DESC)` cho màn lịch sử đồng bộ trên Admin Dashboard. Append-only — job không tự sửa dòng cũ, chỉ tạo dòng mới mỗi lần chạy.

---

## Nhóm 3 — Tri thức dược

### `conditions` (Bảng B)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `name` | |
| `medical_nature` | `benh_ly` / `sinh_ly_binh_thuong` |
| `data_role` | `sinh_hoat_chat_dieu_tri` / `dieu_chinh_thuoc_khac` |
| `icd10_code` | optional |

### `active_ingredient_interactions` (Bảng C) **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `ingredient_a_id` | FK bắt buộc |
| `ingredient_b_id` | FK nullable |
| `ingredient_b_external_name` | nullable |
| `ingredient_b_in_table_a` | `co` / `khong` |
| `interaction_type` | ENUM: `chong_chi_dinh` (tuyệt đối, không xét liều) / `phu_thuoc_lieu` (mức độ thay đổi theo tổng liều/ngày) |
| `severity_level` | 1–4 |
| `handling_type` | `tranh_phoi_hop` / `can_theo_doi` / `cach_gio` / `giam_lieu` |
| `min_interval_hours` | nullable |
| `description` | |
| `source` | |
| `verification_status` | |
| `deleted_at` | **[MỚI]** nullable — xóa mềm |

> Khi `interaction_type = 'chong_chi_dinh'`: dùng trực tiếp `severity_level` và `description` của dòng này, **không cần** tính liều hay tra bảng ngưỡng.
> Khi `interaction_type = 'phu_thuoc_lieu'`: tính tổng liều/ngày rồi tra `active_ingredient_interaction_dose_thresholds`.
> Việc kiểm tra tương tác là **xác định (rule-based)** trên các bảng này; LLM không tham gia (QA.04).
> `InteractionEvaluator` chỉ đọc các dòng `deleted_at IS NULL`.

### `active_ingredient_interaction_dose_thresholds`
*(chỉ áp dụng khi `active_ingredient_interactions.interaction_type = 'phu_thuoc_lieu'`)*

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `interaction_id` | FK → `active_ingredient_interactions.id` |
| `ingredient_ref` | `'A'` hoặc `'B'` — ngưỡng áp dụng cho hoạt chất nào trong cặp |
| `min_dose` | nullable |
| `max_dose` | nullable |
| `dose_unit` | vd `"mg/ngày"` |
| `severity_level` | Ghi đè `severity_level` của bảng C theo ngưỡng liều thực tế |
| `warning_text` | |

### `drug_food_interactions` (Bảng D) **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK |
| `food_to_avoid` | |
| `severity_level` | |
| `reason` | |
| `source` | |
| `verification_status` | |
| `deleted_at` | **[MỚI]** nullable — xóa mềm |

### `active_ingredient_precautions` (Bảng E)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK |
| `condition_id` | FK → `conditions.id` |
| `severity_level` | kèm Chống chỉ định |
| `adjustment_description` | |
| `source` | |
| `verification_status` | |

### `drug_classes` (Bảng F)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `class_name` | |
| `source` | |

### `active_ingredient_drug_classes`
| Cột | Ghi chú |
|---|---|
| `active_ingredient_id` | FK |
| `drug_class_id` | FK |

---

## Nhóm 4 — Tài khoản, consent, liên kết người thân

> **Nguyên tắc vai trò:** "Patient" và "Family Member" là vai trò theo ngữ cảnh, không phải loại tài khoản. Một `user` là Patient với dữ liệu của chính mình, và là Family Member với các patient có `caregiver_links` đang hiệu lực. Vai trò cấp hệ thống chỉ phân biệt `user` / `admin`.

### `users` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `full_name` | |
| `date_of_birth` | |
| `gender` | |
| `phone_number` | nullable, UNIQUE — dùng để đăng nhập bằng SĐT |
| `email` | **[MỚI]** nullable, UNIQUE — dùng để đăng nhập bằng email |
| ~~`senior_mode`~~ | **[XÓA]** Simple Mode chuyển sang lưu cục bộ trên thiết bị (xem ghi chú §12) |
| `system_role` | ENUM: `user` / `admin`, mặc định `user`. Chỉ dùng để cấp quyền vào Admin Dashboard |

> Ràng buộc: **[MỚI]** `CHECK (email IS NOT NULL OR phone_number IS NOT NULL)` — bắt buộc có ít nhất một phương thức đăng nhập. Supabase Auth (`auth.users`) đã có sẵn email/phone dùng để xác thực; cột ở đây là bản sao phục vụ hiển thị/tìm kiếm trong `public.users` mà không phải gọi API admin của Auth.

### `user_consents`
Append-only: mỗi lần đồng ý là một dòng mới; rút consent cập nhật `revoked_at` và `status`, không xóa dòng. Consent thuộc về **data subject** (patient): khi A giám sát B, consent `family_sharing` nằm ở dòng của B.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — chủ thể dữ liệu |
| `consent_type` | ENUM theo mục đích: `health_data` / `family_sharing` / `ai_meal` (mở rộng khi thêm purpose Phase 2) |
| `status` | ENUM: `dong_y` / `thu_hoi` |
| `consented_at` | |
| `revoked_at` | nullable |
| `document_version` | phiên bản văn bản consent đã hiển thị |

> Ràng buộc: tối đa 1 dòng `status = 'dong_y'` cho mỗi `(user_id, consent_type)` (partial unique index).

### `data_deletion_requests`
Phục vụ QA.01, FR09.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `request_type` | ENUM: `xoa_du_lieu` / `rut_consent` |
| `consent_type` | nullable — purpose bị rút (khi `request_type = 'rut_consent'`) |
| `status` | ENUM: `cho_duyet` / `da_duyet` / `tu_choi` / `hoan_tat` |
| `requested_at` | |
| `handled_by_admin_id` | FK → `users.id`, nullable |
| `handled_at` | nullable |
| `rejection_reason` | nullable |

### `caregiver_links`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `patient_user_id` | FK → `users.id` |
| `family_user_id` | FK → `users.id` |
| `status` | ENUM: `pending` / `active` / `revoked` |
| `sharing_enabled` | boolean — công tắc chia sẻ do patient điều khiển |
| `linked_at` | |
| `revoked_at` | nullable |

> Ràng buộc: `UNIQUE(patient_user_id, family_user_id)`; `CHECK(patient_user_id <> family_user_id)`.
> Index: `(family_user_id, status)` cho màn hình "Người thân của tôi"; `(patient_user_id, status)` cho Worker khi tìm người nhận cảnh báo.
> Quan hệ không đối xứng: A giám sát B không cấp quyền nào cho B trên dữ liệu của A.

### `link_codes`
Mã QR / referral do patient tạo để mời người thân (FR07).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `patient_user_id` | FK |
| `code` | UNIQUE |
| `expires_at` | |
| `is_used` | boolean |
| `family_user_id` | FK nullable — người đã dùng mã |

### `device_tokens`
Token FCM để Worker gửi cảnh báo bỏ lỡ liều.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `fcm_token` | UNIQUE |
| `platform` | ENUM: `android` / `ios` |
| `updated_at` | |

### `access_logs` **[SỬA]**
Append-only. Phục vụ NFR06, QA.02, QA.09. Chỉ ghi truy cập của người **khác** patient (family/admin) và các lần bị từ chối; truy cập của chính patient không được ghi.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `actor_user_id` | FK → `users.id` |
| `actor_role` | **[SỬA]** ENUM: `family` / `admin` / `khong_co_quyen` — **tính theo từng lần truy cập** từ quan hệ actor–patient, không đọc từ `users`. `khong_co_quyen` chỉ dùng khi `result = 'denied'` |
| `patient_user_id` | FK → `users.id` |
| `data_scope` | ENUM: `ho_so_suc_khoe` / `danh_sach_thuoc` / `lich_su_tuan_thu` / `canh_bao_tuong_tac` / `goi_y_bua_an` |
| `result` | ENUM: `allowed` / `denied` |
| `rejection_reason` | nullable |
| `accessed_at` | |

> Index: `(patient_user_id, accessed_at)`. Không cấp quyền UPDATE/DELETE cho role ứng dụng.
> Ràng buộc: `CHECK (result = 'allowed' → actor_role IN ('family','admin'))`; `CHECK (actor_user_id <> patient_user_id)` (không có dòng self).

### `dpia_records`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `data_flow_name` | vd `"Gửi điều kiện bệnh nền cho LLM (meal suggestion)"` |
| `has_cross_border_transfer` | boolean |
| `status` | ENUM: `ban_nhap` / `dang_xem_xet` / `da_phe_duyet` |
| `approved_by_id` | FK → `users.id`, nullable |
| `approval_date` | nullable |

---

## Nhóm 5 — Hồ sơ y tế & lịch uống thuốc

### `user_conditions`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `condition_id` | FK |
| `subtype` | nullable — chỉ dùng cho Tiểu đường |
| `stage` | nullable — chỉ dùng cho Suy thận mạn |

### `prescriptions`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `entry_source` | `ocr_scan` / `thu_cong` / `mac_dinh` |
| `prescribed_date` | nullable |
| `prescribing_facility` | nullable |
| `status` | `dang_dung` / `da_ket_thuc` — chỉ `dang_dung` được đưa vào phân tích tương tác |

### `user_medications` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `prescription_id` | FK bắt buộc, không NULL |
| `medication_id` | FK bắt buộc, không NULL — patient chỉ chọn thuốc có sẵn trong danh mục, không nhập tự do |
| `entry_method` | `thu_cong` / `ocr_scan` (quét blister on-device bằng ML Kit) |
| `confirmation_status` | |
| `quantity_per_dose` | Số — vd số viên/ml mỗi lần uống |
| `doses_per_day` | Số — tần suất/ngày |
| `has_interaction_data` | boolean — `false` khi thuốc có trong danh mục nhưng Admin chưa map hoạt chất (dữ liệu danh mục chưa đầy đủ); không còn liên quan tới việc nhập tự do vì trường hợp đó không tồn tại nữa |

> Cả quét vỉ (PB31) lẫn nhập tay (PB10) đều chỉ tạo được dòng khi đã chọn một `medications` cụ thể qua tìm kiếm/gợi ý. Quét không khớp → chuyển sang tìm thủ công (3.05); tìm thủ công không ra → không thêm được thuốc đó vào lịch. Đây là giới hạn Phase 1 đã biết, đổi lại tránh được toàn bộ vấn đề trùng lặp/biến thể chính tả của việc cho nhập tự do.
> `quantity_per_dose × doses_per_day × strength_value` (từ `medication_active_ingredients`) = tổng liều/ngày dùng để tra `active_ingredient_interaction_dose_thresholds`.
> Khi tra tương tác: thuốc có `has_interaction_data = false` (chưa map hoạt chất) được liệt kê riêng cho người dùng biết "thuốc này chưa có dữ liệu để kiểm tra tương tác", tách khỏi các thuốc đã kiểm tra được — không gộp chung với kết quả "không có tương tác" (QA.04, xem PB24).

### `medication_schedules`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_medication_id` | FK |
| `intake_time` | Phục vụ nhắc lịch, **không** dùng trong tính tương tác |
| `days_of_week` | |
| `reminder_enabled` | |

### `dose_logs` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `medication_schedule_id` | FK |
| `scheduled_at` | |
| `taken_at` | |
| `status` | `Đã uống` / `Bỏ lỡ` / `Uống trễ` |
| `client_uuid` | UNIQUE — khóa idempotent do app sinh, chống ghi trùng khi đồng bộ sau offline (QA.08) |
| `synced_at` | nullable — thời điểm bản ghi được đồng bộ lên server |

> Ràng buộc: **[MỚI]** `UNIQUE(medication_schedule_id, scheduled_at)` — mỗi lượt uống (một `medication_schedule_id` tại một `scheduled_at` cụ thể) chỉ có đúng 1 bản ghi. Chống việc Worker (job phát hiện bỏ lỡ, PB20) và Backend (API xác nhận liều, PB13) cùng ghi 2 dòng cho cùng một lượt khi chạy gần nhau.
> Quy tắc ghi khi có xung đột: dùng `INSERT ... ON CONFLICT (medication_schedule_id, scheduled_at) DO UPDATE` — nếu dòng đã tồn tại với `status = 'Bỏ lỡ'` và request xác nhận đến sau đó, cập nhật thành `Uống trễ` cùng `taken_at`; nếu dòng đã có `taken_at` (đã xác nhận), job phát hiện bỏ lỡ **không được ghi đè**. `client_uuid` vẫn giữ vai trò chống gửi trùng từ chính Outbox của Mobile.

### `notifications`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — người nhận |
| `about_patient_user_id` | FK → `users.id` — thông báo nói về patient nào (= `user_id` nếu là nhắc của chính mình) |
| `type` | ENUM: `nhac_uong_thuoc` / `canh_bao_bo_lo_lieu_nguoi_than` |
| `content` | |
| `is_read` | |

### `meal_suggestions`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — patient được gợi ý |
| `suggestion_content` | |
| `based_on_condition` | FK nullable |

---

## Nhóm 6 — Tầng tổng hợp

### `regimen_analysis_snapshots`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `analyzed_at` | |

### `regimen_analysis_findings`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `snapshot_id` | FK |
| `warning_type` | |
| `source_table` | ENUM: `interactions` / `drug_food` / `precautions` / `drug_classes` — bảng nguồn của cảnh báo |
| `source_id` | id bản ghi trong bảng nguồn |
| `is_shown_to_user` | |

### `regimen_analysis_finding_medications`
Thay cho cột "FK nhiều" `related_prescriptions`.

| Cột | Ghi chú |
|---|---|
| `finding_id` | FK → `regimen_analysis_findings.id` |
| `user_medication_id` | FK → `user_medications.id` |

### `user_recommendations`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `finding_id` | FK |
| `is_viewed` | |
| `is_handled` | |

---

## Nhóm 7 — Kiểm thử

### `sample_patient_scenarios` (Bảng G)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `scenario_name` | |
| `expected_result` | |
| `pharmacist_assessment` | |

### `scenario_conditions`
| Cột | Ghi chú |
|---|---|
| `scenario_id` | FK |
| `condition_id` | FK |

### `scenario_active_ingredients`
| Cột | Ghi chú |
|---|---|
| `scenario_id` | FK |
| `active_ingredient_id` | FK |

---

## Quy tắc phân quyền (Backend API)

```
Request của caller C lên dữ liệu của patient P:
  C = P                                   → truy cập của chính chủ: kiểm tra consent purpose
                                            tương ứng của P; KHÔNG ghi access_logs
  tồn tại link(P, C) status = active
    và sharing_enabled = true
    và consent family_sharing của P còn hiệu lực
                                          → actor_role = family
  C.system_role = admin                   → actor_role = admin   (ghi log bắt buộc)
  còn lại                                 → 403 + ghi access_logs: result = denied,
                                            actor_role = khong_co_quyen
```

Mobile App và Admin Web **chỉ gọi Backend API**; chỉ API và Worker truy cập Supabase (bật RLS, không policy cho `anon`/`authenticated`).

---

## Ghi chú thiết kế quan trọng

1. **Chống chỉ định vs. phụ thuộc liều**: `active_ingredient_interactions.interaction_type` tách 2 loại. Chống chỉ định là cảnh báo tuyệt đối, không xét liều; phụ thuộc liều cần tính tổng liều/ngày và tra bảng ngưỡng riêng.
2. **Tính tổng liều/ngày**: dựa trên tần suất uống thực tế (`quantity_per_dose × doses_per_day`) nhân hàm lượng mỗi đơn vị (`medication_active_ingredients.strength_value`), không phải hàm lượng ghi trên nhãn.
3. **`intake_time`** chỉ phục vụ nhắc lịch, tách hoàn toàn khỏi logic kiểm tra tương tác.
4. **Vai trò theo ngữ cảnh**: không lưu Patient/Family Member trên `users`; suy ra từ `caregiver_links` tại thời điểm truy cập và ghi vào `access_logs.actor_role` (chỉ với truy cập của family/admin và các lần bị từ chối; truy cập của chính patient không ghi log).
5. **Consent theo chủ thể dữ liệu**: consent `family_sharing` do patient cấp; consent append-only để có lịch sử phục vụ DPIA. "Đồng ý chia sẻ với một người thân cụ thể" là `caregiver_links.sharing_enabled` của đúng dòng link đó, không phải một dòng `user_consents` riêng — vì consent là theo mục đích xử lý (purpose), còn công tắc chia sẻ là theo từng mối liên kết.
6. **Offline**: `dose_logs.client_uuid` đảm bảo đồng bộ lặp lại không tạo bản ghi trùng; `UNIQUE(medication_schedule_id, scheduled_at)` **[MỚI]** đảm bảo Worker và API không cùng ghi 2 dòng cho một lượt uống.
7. Các cột hành chính (số giấy phép lưu hành, ngày hết hạn, tuổi thọ sản phẩm, trạng thái lưu hành) đã loại khỏi `medications` vì không phục vụ nhắc thuốc hay cảnh báo tương tác trong scope hiện tại.
8. Đã bỏ tính năng AI hỏi đáp: không có bảng `ai_conversations`/`ai_messages`. Không bảng nào dùng pgvector; nếu không có kế hoạch dùng trong Phase 1 thì bỏ khỏi §10 hoặc ghi "reserved for Phase 2".
9. **[MỚI] Xóa mềm danh mục**: `medications`, `active_ingredient_interactions`, `drug_food_interactions` dùng `deleted_at` (nullable). Truy vấn ứng dụng luôn lọc `deleted_at IS NULL`; bản ghi có tham chiếu lịch sử (`user_medications`, `regimen_analysis_findings`...) không bao giờ bị xóa cứng, chỉ đánh dấu xóa mềm.
10. **[MỚI] Nhật ký đồng bộ**: mỗi lượt chạy job đồng bộ danh mục (PB06) tạo một dòng `catalog_sync_runs` (append-only), phục vụ màn lịch sử đồng bộ trên Admin Dashboard và AC "sync log stored with timestamp + record count".
11. ~~Thuốc ngoài danh mục: `medication_id` NULL + `free_text_name`~~ — **đã bỏ ở v4 → v5**: PB04 sẽ được Admin bổ sung đủ thuốc cần dùng, không cần đường nhập tự do cho patient.
12. **[MỚI] Simple Mode là cài đặt cục bộ, không phải dữ liệu server**: bật/tắt lưu bằng `SharedPreferences` (Android) / `UserDefaults` (iOS) ngay trên máy, không qua Backend API, không có bảng nào chứa nó. Lý do: đây là tùy chọn giao diện của người đang cầm máy tại thời điểm đó, không phải thuộc tính của tài khoản hay của patient — lưu ở server sẽ khiến cài đặt "đi theo" tài khoản sang cả những thiết bị/người dùng khác không mong muốn. Hệ quả cho Sprint Backlog: AC của PB33/6.04 ("persists across sessions") vẫn đạt bằng lưu cục bộ; phần "giữ nguyên khi đăng nhập lại" chỉ áp dụng trong phạm vi cùng một thiết bị, không đồng bộ khi đổi máy.
13. **[MỚI] Thuốc không map được hoạt chất vẫn hiển thị riêng khi tra tương tác**: dù `user_medications.medication_id` giờ luôn trỏ tới danh mục, một thuốc trong danh mục vẫn có thể chưa được Admin gán hoạt chất (`has_interaction_data = false`, dữ liệu danh mục chưa đầy đủ). `InteractionEvaluator` phải liệt kê rõ nhóm thuốc này riêng biệt (kèm thông báo "chưa có dữ liệu để kiểm tra"), không gộp chung với nhóm "đã kiểm tra, không thấy tương tác" — giữ đúng nguyên tắc 3 trạng thái của QA.04.
14. **[MỚI] Không có Apple Developer Program trong Phase 1**: hệ quả không nằm ở cấu trúc bảng mà ở tầng vận hành — `device_tokens.platform='ios'` vẫn hợp lệ về mặt dữ liệu (app vẫn xin được token FCM), nhưng Backend/Worker cần biết là gửi push tới token này **sẽ không tới máy** vì APNs chưa được cấu hình (cần tài khoản trả phí). Team cần quyết định một trong hai hướng cho PB20 trên iOS: (a) chấp nhận đây là giới hạn đã biết của Phase 1 và ghi vào tài liệu bàn giao/risk register, người thân dùng iOS chỉ thấy cảnh báo khi tự mở app; hoặc (b) bổ sung task cho Mobile tự động làm mới (poll) danh sách cảnh báo mỗi khi app mở lên/vào foreground, để giảm bớt ảnh hưởng dù không real-time.

---

## Phụ lục — Bảng đối chiếu tên cũ → tên mới (v7 → v8)

Chỉ liệt kê cột có đổi tên. `id`, các FK đã tiếng Anh, `deleted_at`, `client_uuid`, `atc_code`, `icd10_code`, `alias_text`... giữ nguyên.

| Bảng cũ → mới | Cột cũ → mới |
|---|---|
| `medications` | `ten_thuoc` → `name`; `hoat_chat_raw` → `raw_active_ingredient`; `ham_luong` → `strength_text`; `dang_bao_che` → `dosage_form`; `cty_san_xuat_ten` → `manufacturer_name`; `cty_san_xuat_nuoc` → `manufacturer_country`; `quy_cach_dong_goi` → `packaging_spec` |
| `active_ingredients` | `ten_hoat_chat_chuan` → `standard_name`; `vai_tro` → `role`; `nhom_benh` → `disease_group`; `nhom_duoc_ly` → `pharmacological_group`; `nguon` → `source` |
| `medication_active_ingredients` | `ham_luong_value` → `strength_value`; `ham_luong_unit` → `strength_unit`; `don_vi_dinh_luong` → `dosing_unit` |
| `active_ingredient_nhom_benh` → `active_ingredient_disease_groups` | `nhom_benh` → `disease_group` |
| `catalog_sync_runs` | `nguon` → `source`; `bat_dau_luc` → `started_at`; `ket_thuc_luc` → `finished_at`; `trang_thai` → `status`; `so_ban_ghi_them` → `records_inserted`; `so_ban_ghi_cap_nhat` → `records_updated`; `so_ban_ghi_loi` → `records_failed`; `chi_tiet_loi` → `error_details`; `kich_hoat_boi` → `triggered_by` |
| `conditions` | `ten` → `name`; `ban_chat_y_khoa` → `medical_nature`; `vai_tro_du_lieu` → `data_role` |
| `active_ingredient_interactions` | `hoat_chat_a_id` → `ingredient_a_id`; `hoat_chat_b_id` → `ingredient_b_id`; `hoat_chat_b_ten_ngoai` → `ingredient_b_external_name`; `hoat_chat_b_trong_bang_a` → `ingredient_b_in_table_a`; `loai_tuong_tac` → `interaction_type`; `muc_do` → `severity_level`; `loai_xu_ly` → `handling_type`; `khoang_cach_toi_thieu_gio` → `min_interval_hours`; `mo_ta` → `description`; `nguon` → `source`; `trang_thai_xac_minh` → `verification_status` |
| `active_ingredient_interaction_dose_thresholds` | `lieu_toi_thieu` → `min_dose`; `lieu_toi_da` → `max_dose`; `don_vi_lieu` → `dose_unit`; `muc_do` → `severity_level`; `canh_bao_text` → `warning_text` |
| `drug_food_interactions` | `hoat_chat_id` → `active_ingredient_id`; `thuc_pham_can_tranh` → `food_to_avoid`; `muc_do` → `severity_level`; `ly_do` → `reason`; `nguon` → `source`; `trang_thai_xac_minh` → `verification_status` |
| `active_ingredient_precautions` | `hoat_chat_id` → `active_ingredient_id`; `dieu_kien_id` → `condition_id`; `muc_do` → `severity_level`; `mo_ta_dieu_chinh` → `adjustment_description`; `nguon` → `source`; `trang_thai_xac_minh` → `verification_status` |
| `drug_classes` | `ten_nhom` → `class_name`; `nguon` → `source` |
| `users` | `ho_ten` → `full_name`; `ngay_sinh` → `date_of_birth`; `gioi_tinh` → `gender`; `so_dien_thoai` → `phone_number`; `che_do_nguoi_cao_tuoi` → `senior_mode`; `vai_tro_he_thong` → `system_role` |
| `user_consents` | `loai_dong_y` → `consent_type`; `trang_thai` → `status`; `thoi_gian_dong_y` → `consented_at`; `thoi_gian_thu_hoi` → `revoked_at`; `phien_ban_van_ban` → `document_version` |
| `data_deletion_requests` | `loai` → `request_type`; `loai_dong_y` → `consent_type`; `trang_thai` → `status`; `thoi_gian_yeu_cau` → `requested_at`; `admin_xu_ly_id` → `handled_by_admin_id`; `thoi_gian_xu_ly` → `handled_at`; `ly_do_tu_choi` → `rejection_reason` |
| `caregiver_links` | `trang_thai` → `status`; `cho_phep_chia_se` → `sharing_enabled`; `thoi_gian_lien_ket` → `linked_at`; `thoi_gian_thu_hoi` → `revoked_at` |
| `link_codes` | `ma` → `code`; `het_han_luc` → `expires_at`; `da_dung` → `is_used` |
| `device_tokens` | `cap_nhat_luc` → `updated_at` |
| `access_logs` | `ket_qua` → `result`; `ly_do_tu_choi` → `rejection_reason`; `thoi_gian` → `accessed_at` |
| `dpia_records` | `ten_luong_du_lieu` → `data_flow_name`; `co_chuyen_du_lieu_xuyen_bien_gioi` → `has_cross_border_transfer`; `trang_thai` → `status`; `nguoi_phe_duyet_id` → `approved_by_id`; `ngay_phe_duyet` → `approval_date` |
| `user_conditions` | `phan_do` → `stage` |
| `don_thuoc` → `prescriptions` | `nguon_nhap` → `entry_source`; `ngay_ke_don` → `prescribed_date`; `noi_ke_don` → `prescribing_facility`; `trang_thai` → `status` |
| `user_medications` | `don_thuoc_id` → `prescription_id`; `cach_nhap` → `entry_method`; `trang_thai_xac_nhan` → `confirmation_status`; `so_luong_moi_lan` → `quantity_per_dose`; `so_lan_moi_ngay` → `doses_per_day`; `co_du_lieu_tuong_tac` → `has_interaction_data` |
| `medication_schedules` | `gio_uong` → `intake_time`; `ngay_trong_tuan` → `days_of_week`; `bat_tat_nhac` → `reminder_enabled` |
| `dose_logs` | `thoi_gian_du_kien` → `scheduled_at`; `thoi_gian_thuc_uong` → `taken_at`; `trang_thai` → `status`; `dong_bo_luc` → `synced_at` |
| `notifications` | `ve_patient_user_id` → `about_patient_user_id`; `loai` → `type`; `noi_dung` → `content`; `da_doc` → `is_read` |
| `meal_suggestions` | `noi_dung_goi_y` → `suggestion_content`; `dua_tren_dieu_kien` → `based_on_condition` |
| `regimen_analysis_snapshots` | `thoi_gian_phan_tich` → `analyzed_at` |
| `regimen_analysis_findings` | `loai_canh_bao` → `warning_type`; `nguon_bang` → `source_table`; `nguon_id` → `source_id`; `hien_thi_cho_nguoi_dung` → `is_shown_to_user` |
| `user_recommendations` | `da_xem` → `is_viewed`; `da_xu_ly` → `is_handled` |
| `kich_ban_benh_nhan_mau` → `sample_patient_scenarios` | `ten_kich_ban` → `scenario_name`; `ket_qua_ky_vong` → `expected_result`; `danh_gia_duoc_si` → `pharmacist_assessment` |
| `kich_ban_dieu_kien` → `scenario_conditions` | `kich_ban_id` → `scenario_id`; `dieu_kien_id` → `condition_id` |
| `kich_ban_hoat_chat` → `scenario_active_ingredients` | `kich_ban_id` → `scenario_id`; `hoat_chat_id` → `active_ingredient_id` |

Bảng không có cột nào đổi tên: `ingredient_aliases`, `active_ingredient_drug_classes`, `regimen_analysis_finding_medications`.

Các cột đã bỏ/nhắc trong lịch sử: `che_do_nguoi_cao_tuoi` → `senior_mode` (đã xóa ở v2 → v3), `ten_tu_nhap` → `free_text_name` (đã bỏ ở v5), `don_thuoc_lien_quan` → `related_prescriptions` (thiết kế cũ, đã thay bằng `regimen_analysis_finding_medications`).
