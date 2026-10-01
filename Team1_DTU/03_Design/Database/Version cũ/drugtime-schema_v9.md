# DrugTime — Schema Cơ Sở Dữ Liệu (Bản Chốt v9)

Capstone Project 1 (C1SE.07), International School, Đại học Duy Tân.

Căn cứ: ATAM (CD1–CD10), Quality Attributes QA.01–QA.11, `DrugTime_C4_Container_Component_Spec.md` v1.0.

Ký hiệu thay đổi: **[MỚI]** = bảng/cột/ràng buộc mới, **[SỬA]** = đã chỉnh, **[XÓA]** = đã loại bỏ. Từ v9, ký hiệu **chỉ đánh dấu thay đổi v8 → v9**; các ký hiệu của những vòng trước đã được gỡ để tránh nhầm lẫn (chi tiết các vòng trước xem Lịch sử thay đổi).

Mỗi bảng ghi **module sở hữu** (theo C4 spec, mục 2.1). Chỉ module sở hữu được đọc/ghi trực tiếp bảng đó; module khác truy cập qua `<module>.api`. FK giữa các bảng thuộc module khác nhau vẫn được phép ở tầng DB.

## Lịch sử thay đổi

### v8 → v9 (bản này)

Phát sinh từ ATAM §3 và C4 spec (CD1, CD2, CD6, CD8, CD9, CD10):

1. **Lịch mới/sửa không bị quét thành bỏ lỡ** — thêm `medication_schedules.effective_from` (CD6, rủi ro 2).
2. **Trạng thái Worker nằm trong DB** — thêm Nhóm 8 gồm `missed_dose_scan_cursor` (con trỏ quét, CD6) và `worker_heartbeats` (CD4, CD10).
3. **Chống trùng cảnh báo** — thêm `notifications.dedupe_key` (UNIQUE) và `notifications.created_at` (CD6).
4. **Nhóm bệnh là dữ liệu, không phải ENUM** — thêm bảng lookup `disease_groups`. `active_ingredient_disease_groups.disease_group` (ENUM) đổi thành `disease_group_id` (FK). Bỏ `active_ingredients.disease_group` vì trùng vai trò với bảng nối (một hoạt chất có thể thuộc nhiều nhóm) — bảng nối là nguồn duy nhất (CD8, QA.10).
5. **Rút consent không qua hàng đợi** — bỏ `data_deletion_requests.request_type` (chỉ còn một giá trị `xoa_du_lieu` nên cột không còn ý nghĩa) và `consent_type`. Rút consent ghi thẳng vào `user_consents` và có hiệu lực ngay (QA.01).
6. **Thực thi xóa dữ liệu** — thêm `data_deletion_requests.completed_at`, `last_error`; thêm `users.erased_at` và ràng buộc tombstone; thêm mục "Quy trình xóa dữ liệu" (CD9).
7. **Index cho truy vấn theo người truy cập** — thêm `access_logs(actor_user_id, accessed_at)` (QA.09, Admin review).
8. **Hai DB role riêng** — thêm mục "Role cơ sở dữ liệu và quyền" cho `api_role`, `worker_role` (CD1, CD9).
9. **Làm rõ `catalog_sync_runs`** — job chỉ cập nhật dòng của lượt chạy hiện tại (để ghi `finished_at`, `status`), không bao giờ sửa dòng của lượt trước. Câu "append-only" ở v8 mâu thuẫn với cột `finished_at` nullable.
10. **Quyết định cho iOS (ghi chú 14 cũ)** — chọn hướng (b): app kéo danh sách cảnh báo khi mở/vào foreground. Push chỉ mang nội dung tối thiểu; nội dung chi tiết đọc qua API và được ghi `access_logs` (CD6 bổ sung).
11. **Làm rõ `dose_logs`** — `client_uuid` và `taken_at` là nullable vì dòng `Bỏ lỡ` do Worker tạo không có hai giá trị này (v8 chưa ghi rõ).
12. **Đăng nhập bằng OTP** — bỏ mật khẩu và luồng quên mật khẩu. Không đổi cấu trúc bảng (mật khẩu vốn chỉ nằm ở Supabase Auth); bổ sung ghi chú cho `users` về việc tạo dòng ở lần đăng nhập đầu và định dạng SĐT.
13. **Sửa tham chiếu chéo cũ** theo đánh số QA/NFR hiện hành: log truy cập là NFR05 (không phải NFR06); xác nhận liều là QA.04/NFR03 (không phải QA.05/NFR04); kiểm tra tương tác 3 trạng thái dẫn FR04/CD7 (không phải QA.04); `data_deletion_requests` phục vụ QA.01/NFR01 (không phải FR09).

Migrate (theo thứ tự):
- Tạo `disease_groups` và seed từ các giá trị ENUM cũ → thêm `active_ingredient_disease_groups.disease_group_id`, điền theo ENUM cũ → chuyển dữ liệu `active_ingredients.disease_group` (nếu có) thành dòng bảng nối → xóa hai cột cũ và kiểu ENUM.
- Thêm `medication_schedules.effective_from` với giá trị ban đầu = thời điểm migrate.
- Xóa (hoặc xử lý thủ công) các dòng `data_deletion_requests.request_type = 'rut_consent'` trước khi bỏ cột.
- Thêm `notifications.created_at` (giá trị ban đầu = thời điểm migrate) và `dedupe_key` (NULL cho dòng cũ).
- Nới ràng buộc NOT NULL (nếu có) trên `users.full_name`, `date_of_birth`, `gender` để tombstone hợp lệ.
- Tạo `api_role`, `worker_role`, policy RLS và GRANT như mục "Role cơ sở dữ liệu và quyền".

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

1. **`access_logs` không còn ghi truy cập `self`** — NFR05 và QA.09 chỉ yêu cầu log truy cập của Family Member và Admin; patient xem dữ liệu của chính mình nằm ngoài yêu cầu, và ghi mọi lần mở màn hình/xác nhận liều làm bảng phình to, thêm một lần ghi đồng bộ trên đường xác nhận liều (QA.04, NFR03). → `actor_role` đổi từ `self / family / admin` thành `family / admin / khong_co_quyen`. Nhánh `C = P` trong quy tắc phân quyền vẫn kiểm tra consent của P (QA.01) nhưng **không ghi** `access_logs`.
2. **Giá trị `khong_co_quyen`** — chỉ dùng cho dòng `result = 'denied'`, để vẫn log được người không phải family/admin (đã unlink, bị thu hồi quyền, sửa patient ID trong request — QA.02, QA.09). Thêm `CHECK (result = 'allowed' → actor_role IN ('family','admin'))`.

Hệ quả: request bị từ chối do chính patient đã rút consent (QA.01) không để lại dòng log. Migrate: xóa các dòng `actor_role = 'self'` (nếu có) trước khi đổi ENUM.

### v7 → v8

1. **Tên bảng và tên cột chuyển toàn bộ sang tiếng Anh** (snake_case). Các phần còn lại giữ tiếng Việt: mô tả, ghi chú, và **giá trị ENUM** (vd `dong_y`, `cho_duyet`, `chong_chi_dinh`, `Đã uống`) — giá trị ENUM là dữ liệu, không phải tên định danh, nên không đổi.
2. **Chỉ đổi tên, không đổi cấu trúc, kiểu dữ liệu hay ràng buộc.** Bảng đối chiếu đầy đủ tên cũ → tên mới ở Phụ lục cuối tài liệu. Các tên nhắc trong lịch sử thay đổi (v2 → v7) đã được cập nhật theo tên mới để tài liệu nhất quán.
3. Bảng đổi tên: `don_thuoc` → `prescriptions`, `active_ingredient_nhom_benh` → `active_ingredient_disease_groups`, `kich_ban_benh_nhan_mau` → `sample_patient_scenarios`, `kich_ban_dieu_kien` → `scenario_conditions`, `kich_ban_hoat_chat` → `scenario_active_ingredients`. Các bảng còn lại vốn đã có tên tiếng Anh.
4. `access_logs.ly_do_tu_choi` và `data_deletion_requests.ly_do_tu_choi` cùng đổi thành `rejection_reason` (cùng nghĩa, giữ đặt tên nhất quán).
5. Migrate: dùng `ALTER TABLE ... RENAME TO` / `RENAME COLUMN` (đổi tên không mất dữ liệu). Cần cập nhật đồng thời code Backend/Worker, RLS, index, constraint, seed/ETL script và các tài liệu tham chiếu tên cũ (`drugtime_mobile_backend_components.md`, Sprint Backlog).


---

## Nhóm 1 — Danh mục thuốc
Module sở hữu: `catalog`.

### `medications`
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
| `deleted_at` | nullable — xóa mềm; NULL = đang lưu hành trong ứng dụng |

> Mọi truy vấn của Mobile/Admin (trừ màn quản trị "xem đã xóa") phải lọc `deleted_at IS NULL`. Bản ghi có `deleted_at` khác NULL vẫn được `medication_active_ingredients`, `user_medications` tham chiếu để giữ lịch sử — không xóa cứng khi còn tham chiếu.

### `active_ingredients` (Bảng A) **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `standard_name` | |
| `role` | ENUM: `dieu_tri_benh_nen` / `trieu_chung_cap_tinh` |
| ~~`disease_group`~~ | **[XÓA]** Nhóm bệnh chỉ lưu ở `active_ingredient_disease_groups` |
| `pharmacological_group` | |
| `atc_code` | |
| `source` | |

### `ingredient_aliases`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK → `active_ingredients.id` |
| `alias_text` | Tên gọi khác (thương mại, viết tắt, tiếng Anh/Việt...) |

### `disease_groups` **[MỚI]**
Bảng lookup do Admin quản lý. Thêm nhóm bệnh ở Phase 2 = thêm dòng, không sửa ENUM hay nhánh code (QA.10, CD8).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `code` | UNIQUE — mã ổn định dùng trong cấu hình, vd `tang_huyet_ap`, `tieu_duong` |
| `name` | Tên hiển thị |
| `is_active` | boolean, mặc định `true` — tắt thay vì xóa khi còn tham chiếu |

---

## Nhóm 2 — Lớp nối ETL
Module sở hữu: `catalog`.

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

### `active_ingredient_disease_groups` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK → `active_ingredients.id` |
| `disease_group_id` | **[SỬA]** FK → `disease_groups.id` (thay cho cột ENUM `disease_group`) |

> Ràng buộc: **[MỚI]** `UNIQUE(active_ingredient_id, disease_group_id)`.

### `catalog_sync_runs` **[SỬA]**
Phục vụ PB06 (nhật ký đồng bộ danh mục từ Nguồn dữ liệu quản lý dược Việt Nam).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `source` | ENUM: `dav_drugbank` / `qd_5948` / `duoc_thu_qg` — nguồn nào được đồng bộ |
| `started_at` | |
| `finished_at` | nullable — NULL khi lượt chạy chưa kết thúc hoặc bị treo |
| `status` | ENUM: `dang_chay` / `thanh_cong` / `that_bai` |
| `records_inserted` | mặc định 0 |
| `records_updated` | mặc định 0 |
| `records_failed` | mặc định 0 |
| `error_details` | nullable — text/JSON tóm tắt các bản ghi lỗi (không lưu toàn bộ payload) |
| `triggered_by` | ENUM: `scheduler` / `admin_thu_cong` — `scheduler` khi chạy từ tick (`catalog.sync_if_due()`), `admin_thu_cong` khi Admin kích hoạt |

> Index: `(source, started_at DESC)` cho màn lịch sử đồng bộ trên Admin Dashboard.
> **[SỬA]** Mỗi lượt chạy tạo một dòng mới (`dang_chay`) và chỉ cập nhật chính dòng đó khi kết thúc (`finished_at`, `status`, số bản ghi). Dòng của các lượt trước không bao giờ bị sửa.
> `catalog.sync_if_due()` đọc lượt `thanh_cong` gần nhất theo từng `source` để quyết định có cần chạy không (tính theo giờ Asia/Ho_Chi_Minh, CD10).

---

## Nhóm 3 — Tri thức dược
Module sở hữu: `catalog` cho `conditions`, `drug_classes`, `active_ingredient_drug_classes`; `interaction` cho các bảng quy tắc (C, ngưỡng liều, D, E).

### `conditions` (Bảng B) — `catalog`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `name` | |
| `medical_nature` | `benh_ly` / `sinh_ly_binh_thuong` |
| `data_role` | `sinh_hoat_chat_dieu_tri` / `dieu_chinh_thuoc_khac` |
| `icd10_code` | optional |

### `active_ingredient_interactions` (Bảng C) — `interaction`
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
| `deleted_at` | nullable — xóa mềm |

> Khi `interaction_type = 'chong_chi_dinh'`: dùng trực tiếp `severity_level` và `description` của dòng này, **không cần** tính liều hay tra bảng ngưỡng.
> Khi `interaction_type = 'phu_thuoc_lieu'`: tính tổng liều/ngày rồi tra `active_ingredient_interaction_dose_thresholds`.
> Việc kiểm tra tương tác là **xác định (rule-based)** trên các bảng này; LLM không tham gia (FR04, CD7).
> `InteractionEvaluator` chỉ đọc các dòng `deleted_at IS NULL`.

### `active_ingredient_interaction_dose_thresholds` — `interaction`
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

### `drug_food_interactions` (Bảng D) — `interaction`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK |
| `food_to_avoid` | |
| `severity_level` | |
| `reason` | |
| `source` | |
| `verification_status` | |
| `deleted_at` | nullable — xóa mềm |

> `ai_meal` dùng bảng này (qua `interaction.api`) để lọc món do LLM gợi ý.

### `active_ingredient_precautions` (Bảng E) — `interaction`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK |
| `condition_id` | FK → `conditions.id` |
| `severity_level` | kèm Chống chỉ định |
| `adjustment_description` | |
| `source` | |
| `verification_status` | |

### `drug_classes` (Bảng F) — `catalog`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `class_name` | |
| `source` | |

### `active_ingredient_drug_classes` — `catalog`
| Cột | Ghi chú |
|---|---|
| `active_ingredient_id` | FK |
| `drug_class_id` | FK |

---

## Nhóm 4 — Tài khoản, consent, liên kết người thân

> **Nguyên tắc vai trò:** "Patient" và "Family Member" là vai trò theo ngữ cảnh, không phải loại tài khoản. Một `user` là Patient với dữ liệu của chính mình, và là Family Member với các patient có `caregiver_links` đang hiệu lực. Vai trò cấp hệ thống chỉ phân biệt `user` / `admin`.

### `users` **[SỬA]** — `identity`
| Cột | Ghi chú |
|---|---|
| `id` | PK — trùng `auth.users.id` của Supabase Auth |
| `full_name` | **[SỬA]** nullable — NULL trước khi hoàn tất hồ sơ và sau khi xóa dữ liệu |
| `date_of_birth` | **[SỬA]** nullable — NULL trước khi hoàn tất hồ sơ và sau khi xóa dữ liệu |
| `gender` | **[SỬA]** nullable — NULL trước khi hoàn tất hồ sơ và sau khi xóa dữ liệu |
| `phone_number` | nullable, UNIQUE — dùng để đăng nhập bằng SĐT |
| `email` | nullable, UNIQUE — dùng để đăng nhập bằng email |
| `system_role` | ENUM: `user` / `admin`, mặc định `user`. Chỉ dùng để cấp quyền vào Admin Dashboard |
| `erased_at` | **[MỚI]** timestamptz, nullable — khác NULL nghĩa là dòng đã thành tombstone (CD9) |

> Ràng buộc:
> - **[SỬA]** `CHECK (erased_at IS NOT NULL OR email IS NOT NULL OR phone_number IS NOT NULL)` — tài khoản đang hoạt động phải có ít nhất một phương thức đăng nhập.
> - **[MỚI]** `CHECK (erased_at IS NULL OR (full_name IS NULL AND date_of_birth IS NULL AND gender IS NULL AND email IS NULL AND phone_number IS NULL))` — tombstone không còn PII.
>
> Supabase Auth (`auth.users`) đã có sẵn email/phone dùng để xác thực; cột ở đây là bản sao phục vụ hiển thị/tìm kiếm trong `public.users` mà không phải gọi API admin của Auth.
> **[MỚI]** Đăng nhập bằng OTP qua SĐT hoặc email, không có mật khẩu. Dòng `users` được tạo ở lần xác thực OTP đầu tiên, chỉ với `phone_number` hoặc `email`; `full_name`, `date_of_birth`, `gender` được điền ở màn hồ sơ sau đó (vì vậy các cột này nullable ngay cả khi chưa xóa dữ liệu). `phone_number` lưu theo định dạng E.164 (vd `+84901234567`) để khớp với Supabase Auth.
> **[MỚI]** Sau khi xóa dữ liệu, tài khoản Auth cũng bị xóa; nếu người đó đăng nhập lại bằng cùng SĐT/email thì là tài khoản mới với `id` mới. Tombstone có PII = NULL nên không vướng UNIQUE.
> **[MỚI]** Dòng tombstone được giữ để `access_logs`, `user_consents`, `data_deletion_requests` còn tham chiếu hợp lệ. Xác thực và đăng nhập từ chối user có `erased_at` (401).

### `user_consents` — `consent`
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
> Rút consent ghi trực tiếp vào bảng này và có hiệu lực ở request kế tiếp (QA.01, CD2) — không đi qua `data_deletion_requests`.
> **[MỚI]** Được giữ lại sau khi xóa dữ liệu, làm bằng chứng căn cứ xử lý (CD9).

### `data_deletion_requests` **[SỬA]** — `consent`
Phục vụ QA.01, NFR01. Chỉ dùng cho yêu cầu xóa dữ liệu (cần Admin duyệt).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — người yêu cầu xóa |
| ~~`request_type`~~ | **[XÓA]** Chỉ còn một loại yêu cầu |
| ~~`consent_type`~~ | **[XÓA]** Rút consent không đi qua bảng này |
| `status` | ENUM: `cho_duyet` / `da_duyet` / `tu_choi` / `hoan_tat` |
| `requested_at` | |
| `handled_by_admin_id` | FK → `users.id`, nullable — Admin duyệt/từ chối |
| `handled_at` | nullable — thời điểm Admin duyệt/từ chối |
| `rejection_reason` | nullable |
| `completed_at` | **[MỚI]** nullable — thời điểm Worker hoàn tất cả hai bước xóa |
| `last_error` | **[MỚI]** nullable — lỗi gần nhất khi thực thi (vd Supabase Auth không phản hồi); xóa về NULL khi hoàn tất |

> Luồng trạng thái: `cho_duyet` → `da_duyet` → `hoan_tat`, hoặc `cho_duyet` → `tu_choi`.
> Ràng buộc **[MỚI]**:
> - `CHECK (status <> 'tu_choi' OR rejection_reason IS NOT NULL)`
> - `CHECK (status <> 'hoan_tat' OR completed_at IS NOT NULL)`
> - Partial unique index: tối đa 1 yêu cầu đang mở (`status IN ('cho_duyet','da_duyet')`) cho mỗi `user_id`.
>
> Index **[MỚI]**: `(status, requested_at)` cho hàng đợi của Admin và cho `consent.resume_erasures()` (tìm dòng `da_duyet`).
> Được giữ lại sau khi xóa dữ liệu, làm bằng chứng đã thực hiện (CD9).

### `caregiver_links` — `family`
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

### `link_codes` — `family`
Mã QR / referral do patient tạo để mời người thân (FR07).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `patient_user_id` | FK |
| `code` | UNIQUE |
| `expires_at` | |
| `is_used` | boolean |
| `family_user_id` | FK nullable — người đã dùng mã |

### `device_tokens` — `identity`
Token FCM để Worker gửi cảnh báo bỏ lỡ liều.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `fcm_token` | UNIQUE |
| `platform` | ENUM: `android` / `ios` |
| `updated_at` | |

> Token `ios` vẫn được lưu nhưng Worker bỏ qua khi gửi push (không có APNs trong Phase 1, xem ghi chú 14).

### `access_logs` **[SỬA]** — `access`
Append-only. Phục vụ NFR05, QA.02, QA.09. Chỉ ghi truy cập của người **khác** patient (family/admin) và các lần bị từ chối; truy cập của chính patient không được ghi. Chỉ Backend API ghi bảng này (một điểm ghi duy nhất, CD1); Worker không ghi.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `actor_user_id` | FK → `users.id` |
| `actor_role` | ENUM: `family` / `admin` / `khong_co_quyen` — **tính theo từng lần truy cập** từ quan hệ actor–patient, không đọc từ `users`. `khong_co_quyen` chỉ dùng khi `result = 'denied'` |
| `patient_user_id` | FK → `users.id` |
| `data_scope` | ENUM: `ho_so_suc_khoe` / `danh_sach_thuoc` / `lich_su_tuan_thu` / `canh_bao_tuong_tac` / `goi_y_bua_an` |
| `result` | ENUM: `allowed` / `denied` |
| `rejection_reason` | nullable |
| `accessed_at` | |

> Index: `(patient_user_id, accessed_at)`; **[MỚI]** `(actor_user_id, accessed_at)` cho màn Admin xem lịch sử truy cập theo người.
> Ràng buộc: `CHECK (result = 'allowed' → actor_role IN ('family','admin'))`; `CHECK (actor_user_id <> patient_user_id)` (không có dòng self).
> Không role nào có quyền UPDATE/DELETE. Được giữ lại sau khi xóa dữ liệu, tham chiếu tới tombstone (CD9).
> Người thân đọc nội dung cảnh báo bỏ lỡ liều (qua API) được ghi với `data_scope = 'lich_su_tuan_thu'`.

### `dpia_records` — `consent`
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
Module sở hữu: `medication` cho `user_conditions`, `prescriptions`, `user_medications`, `medication_schedules`; `adherence` cho `dose_logs`, `notifications`; `ai_meal` cho `meal_suggestions`.

### `user_conditions` — `medication`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `condition_id` | FK |
| `subtype` | nullable — chỉ dùng cho Tiểu đường |
| `stage` | nullable — chỉ dùng cho Suy thận mạn |

### `prescriptions` — `medication`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `entry_source` | `ocr_scan` / `thu_cong` / `mac_dinh` |
| `prescribed_date` | nullable |
| `prescribing_facility` | nullable |
| `status` | `dang_dung` / `da_ket_thuc` — chỉ `dang_dung` được đưa vào phân tích tương tác |

### `user_medications` — `medication`
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
| `has_interaction_data` | boolean — `false` khi thuốc có trong danh mục nhưng Admin chưa map hoạt chất |

> Cả quét vỉ (PB31) lẫn nhập tay (PB10) đều chỉ tạo được dòng khi đã chọn một `medications` cụ thể qua tìm kiếm/gợi ý. Quét không khớp → chuyển sang tìm thủ công (3.05); tìm thủ công không ra → không thêm được thuốc đó vào lịch. Đây là giới hạn Phase 1 đã biết.
> `quantity_per_dose × doses_per_day × strength_value` (từ `medication_active_ingredients`) = tổng liều/ngày dùng để tra `active_ingredient_interaction_dose_thresholds`.
> Khi tra tương tác: thuốc có `has_interaction_data = false` được liệt kê riêng ("thuốc này chưa có dữ liệu để kiểm tra tương tác"), không gộp với kết quả "không có tương tác" (FR04, CD7, xem PB24).

### `medication_schedules` **[SỬA]** — `medication`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_medication_id` | FK |
| `intake_time` | Giờ địa phương (Asia/Ho_Chi_Minh). Phục vụ nhắc lịch, **không** dùng trong tính tương tác |
| `days_of_week` | |
| `reminder_enabled` | |
| `effective_from` | **[MỚI]** timestamptz, NOT NULL, mặc định `now()` — lượt uống có `scheduled_at` trước mốc này không thuộc lịch hiện tại |

> **[MỚI]** Tạo lịch hoặc sửa `intake_time`/`days_of_week` phải đặt `effective_from = now()`. Worker chỉ quét các lượt có `scheduled_at >= effective_from`, nên lịch mới tạo hoặc mới sửa không bị quét thành bỏ lỡ (CD6, rủi ro 2).
> **[MỚI]** Giả định Phase 1: mọi lịch tính theo giờ Asia/Ho_Chi_Minh. Patient ở múi giờ khác có thể nhận cảnh báo bỏ lỡ sai giờ; nếu cần hỗ trợ, thêm `users.timezone` ở Phase 2.

### `dose_logs` **[SỬA]** — `adherence`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `medication_schedule_id` | FK |
| `scheduled_at` | |
| `taken_at` | **[SỬA]** nullable — NULL với dòng `Bỏ lỡ` |
| `status` | `Đã uống` / `Bỏ lỡ` / `Uống trễ` |
| `client_uuid` | **[SỬA]** UNIQUE, nullable (NULL với dòng do Worker tạo) — khóa idempotent do app sinh, chống ghi trùng khi đồng bộ sau offline (QA.08, CD3) |
| `synced_at` | nullable — thời điểm bản ghi được đồng bộ lên server |

> Ràng buộc: `UNIQUE(medication_schedule_id, scheduled_at)` — mỗi lượt uống chỉ có đúng 1 bản ghi, chống việc Worker (PB20) và API (PB13) cùng ghi 2 dòng cho một lượt.
> Quy tắc ghi khi có xung đột: `INSERT ... ON CONFLICT (medication_schedule_id, scheduled_at) DO UPDATE` — nếu dòng đã tồn tại với `status = 'Bỏ lỡ'` và xác nhận đến sau, cập nhật thành `Uống trễ` cùng `taken_at`; nếu dòng đã có `taken_at`, job phát hiện bỏ lỡ **không được ghi đè**. `client_uuid` chống gửi trùng từ Outbox của Mobile. API từ chối `taken_at` ở tương lai.

### `notifications` **[SỬA]** — `adherence`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — người nhận |
| `about_patient_user_id` | FK → `users.id` — thông báo nói về patient nào |
| `type` | ENUM: `nhac_uong_thuoc` / `canh_bao_bo_lo_lieu_nguoi_than` |
| `content` | Nội dung chi tiết — chỉ trả về qua API sau khi kiểm tra quyền, **không** đưa vào payload push |
| `is_read` | |
| `dedupe_key` | **[MỚI]** UNIQUE, nullable — với cảnh báo bỏ lỡ: `bo_lo:{dose_log_id}:{user_id}`. Worker ghi bằng `ON CONFLICT (dedupe_key) DO NOTHING` |
| `created_at` | **[MỚI]** timestamptz, NOT NULL, mặc định `now()` |

> Index **[MỚI]**: `(user_id, is_read, created_at DESC)` cho hộp thư cảnh báo.
> Payload push chỉ gồm câu báo chung và `notification_id`; app gọi API để lấy nội dung, và lần đọc đó được kiểm tra quyền và ghi `access_logs` (CD6).
> Server không tạo dòng `nhac_uong_thuoc` trong Phase 1 vì nhắc thuốc chạy cục bộ trên thiết bị (CD5); giá trị được giữ cho Phase 2.

### `meal_suggestions` — `ai_meal`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — patient được gợi ý |
| `suggestion_content` | |
| `based_on_condition` | FK nullable |

---

## Nhóm 6 — Tầng tổng hợp
Module sở hữu: `interaction`.

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
Chỉ dùng trong CI (bộ kịch bản kiểm thử engine tương tác, CD7). Không cấp quyền cho `api_role`, `worker_role`.

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

## Nhóm 8 — Vận hành Worker **[MỚI]**

### `missed_dose_scan_cursor` **[MỚI]** — `adherence`
Con trỏ quét bỏ lỡ liều (CD6). Trạng thái nằm trong DB nên mất job ở Redis không làm mất tiến độ quét.

| Cột | Ghi chú |
|---|---|
| `job_name` | PK — vd `missed_dose_scan` |
| `scanned_until` | timestamptz — mốc `scheduled_at` đã quét xong |
| `updated_at` | timestamptz |

> Mỗi lần quét lấy cửa sổ `[scanned_until − overlap, now() − grace_period]`; `overlap` và `grace_period` là cấu hình (SP2). Khoảng chồng lấn an toàn vì UPSERT của `dose_logs` và `dedupe_key` của `notifications` đều idempotent. Cập nhật `scanned_until` là bước cuối của lượt quét (DW1 bước 13).

### `worker_heartbeats` **[MỚI]** — `health`
Heartbeat của Worker (CD4, CD10). `/health` của API đọc bảng này để đánh giá readiness.

| Cột | Ghi chú |
|---|---|
| `worker_name` | PK — vd `drugtime-worker` |
| `last_beat_at` | timestamptz — cập nhật mỗi phút bởi vòng lặp của Scheduler |
| `instance_id` | text — định danh instance đang chạy, giúp phát hiện hai instance cùng chạy |

> Readiness báo lỗi khi `now() − last_beat_at` vượt ngưỡng cấu hình (vd 3 phút).

---

## Quy tắc phân quyền (Backend API) **[SỬA]**

Thực thi tại module `access` (một điểm duy nhất, CD1). Đọc trực tiếp từ `family` và `consent` ở mỗi request, không cache (CD2).

```
Request của caller C lên dữ liệu của patient P:
  C.erased_at IS NOT NULL                 → 401, dừng ngay (không tới bước phân quyền)   [MỚI]
  C = P                                   → truy cập của chính chủ: kiểm tra consent purpose
                                            tương ứng của P; KHÔNG ghi access_logs
  tồn tại link(P, C) status = active
    và sharing_enabled = true
    và consent family_sharing của P còn hiệu lực
                                          → actor_role = family  (ghi log bắt buộc, fail-closed)
  C.system_role = admin                   → actor_role = admin   (ghi log bắt buộc, fail-closed)
  còn lại                                 → 403 + ghi access_logs: result = denied,
                                            actor_role = khong_co_quyen (transaction riêng)
```

**[MỚI]** Worker xác định người nhận cảnh báo bỏ lỡ liều theo đúng điều kiện của nhánh `family` ở trên (qua `access.api`), nhưng không ghi `access_logs` vì không có dữ liệu nào được tiết lộ lúc này: push không chứa nội dung, và nội dung chỉ được đọc qua API (có ghi log).

Mobile App và Admin Web **chỉ gọi Backend API**; chỉ API và Worker truy cập cơ sở dữ liệu (bật RLS, không policy cho `anon`/`authenticated`).

---

## Role cơ sở dữ liệu và quyền **[MỚI]**

Hai role đăng nhập riêng cho hai container (CD1): `api_role` (Backend API), `worker_role` (Background Job Worker). Không container nào dùng `service_role`.

Mọi bảng bật RLS. Không dựa vào `BYPASSRLS`; mỗi bảng có policy cho phép (`USING (true) WITH CHECK (true)`) dành riêng cho role được cấp quyền, còn phạm vi thao tác do `GRANT` quyết định. `anon` và `authenticated` không có policy nào.

Ký hiệu: S = SELECT, I = INSERT, U = UPDATE, D = DELETE, — = không có quyền.

| Bảng | Module | `api_role` | `worker_role` | Ghi chú |
|---|---|---|---|---|
| `medications`, `drug_food_interactions`, `active_ingredient_interactions` | catalog / interaction | S I U | S I U | Có `deleted_at`: xóa mềm bằng UPDATE, không cấp D |
| `active_ingredients`, `ingredient_aliases`, `medication_active_ingredients`, `active_ingredient_disease_groups`, `disease_groups`, `conditions`, `drug_classes`, `active_ingredient_drug_classes`, `active_ingredient_interaction_dose_thresholds`, `active_ingredient_precautions` | catalog / interaction | S I U D | S I U D | Admin CRUD; Worker đồng bộ |
| `catalog_sync_runs` | catalog | S | S I U | Worker chỉ U dòng của lượt đang chạy |
| `users` | identity | S I U | S U | Không role nào có D; Worker U để tạo tombstone |
| `device_tokens` | identity | S I U D | S D | |
| `user_consents` | consent | S I U | S | Giữ lại khi xóa dữ liệu |
| `data_deletion_requests` | consent | S I U | S U | |
| `dpia_records` | consent | S I U | — | |
| `caregiver_links`, `link_codes` | family | S I U D | S U D | Worker D/U khi xóa dữ liệu |
| `access_logs` | access | S I | — | Không role nào có U/D |
| `user_conditions`, `prescriptions`, `user_medications`, `medication_schedules` | medication | S I U D | S D | Worker S để quét, D khi xóa dữ liệu |
| `dose_logs` | adherence | S I U | S I U D | |
| `notifications` | adherence | S U | S I D | API chỉ U `is_read` |
| `meal_suggestions` | ai_meal | S I | S D | |
| `regimen_analysis_snapshots`, `regimen_analysis_findings`, `regimen_analysis_finding_medications`, `user_recommendations` | interaction | S I U | S D | |
| `missed_dose_scan_cursor` | adherence | — | S I U | |
| `worker_heartbeats` | health | S | S I U | |
| Nhóm 7 (kịch bản kiểm thử) | — | — | — | Chỉ dùng trong CI |

---

## Quy trình xóa dữ liệu **[MỚI]**

Thực thi bởi `consent.execute_erasure` trong Worker (CD9, C4 spec DW3). Yêu cầu phải ở trạng thái `da_duyet`.

**Bước A — một transaction.** Theo thứ tự (theo phụ thuộc FK), với P là người yêu cầu:

| # | Module | Xử lý |
|---|---|---|
| 1 | ai_meal | Xóa `meal_suggestions` của P |
| 2 | interaction | Xóa `user_recommendations`, `regimen_analysis_finding_medications`, `regimen_analysis_findings`, `regimen_analysis_snapshots` của P |
| 3 | adherence | Xóa `dose_logs` thuộc lịch của P; xóa `notifications` có `user_id = P` hoặc `about_patient_user_id = P` |
| 4 | medication | Xóa `medication_schedules`, `user_medications`, `prescriptions`, `user_conditions` của P |
| 5 | family | Xóa `caregiver_links` có P ở một trong hai phía; xóa `link_codes` có `patient_user_id = P`; đặt `family_user_id = NULL` ở các `link_codes` P đã dùng |
| 6 | identity | Xóa `device_tokens` của P; chuyển `users` của P thành tombstone (PII = NULL, `erased_at = now()`) |

**Bước B.** `identity` xóa tài khoản trên Supabase Auth (404 coi là thành công).

**Kết thúc.** Chỉ khi cả hai bước xong: `status = 'hoan_tat'`, `completed_at = now()`, `last_error = NULL`. Nếu lỗi: giữ `da_duyet`, ghi `last_error`, và tick kế tiếp chạy lại (`consent.resume_erasures()`). Mọi bước đều idempotent.

**Giữ lại, tham chiếu tới tombstone:** `access_logs` (trách nhiệm giải trình), `user_consents` (bằng chứng căn cứ xử lý), `data_deletion_requests` (bằng chứng đã thực hiện). Căn cứ pháp lý của việc giữ lại phải được ghi trong DPIA và được mentor duyệt.

---

## Ghi chú thiết kế quan trọng

1. **Chống chỉ định vs. phụ thuộc liều**: `active_ingredient_interactions.interaction_type` tách 2 loại. Chống chỉ định là cảnh báo tuyệt đối, không xét liều; phụ thuộc liều cần tính tổng liều/ngày và tra bảng ngưỡng riêng.
2. **Tính tổng liều/ngày**: dựa trên tần suất uống thực tế (`quantity_per_dose × doses_per_day`) nhân hàm lượng mỗi đơn vị (`medication_active_ingredients.strength_value`), không phải hàm lượng ghi trên nhãn.
3. **`intake_time`** chỉ phục vụ nhắc lịch, tách hoàn toàn khỏi logic kiểm tra tương tác.
4. **Vai trò theo ngữ cảnh**: không lưu Patient/Family Member trên `users`; suy ra từ `caregiver_links` tại thời điểm truy cập và ghi vào `access_logs.actor_role` (chỉ với truy cập của family/admin và các lần bị từ chối).
5. **Consent theo chủ thể dữ liệu**: consent `family_sharing` do patient cấp; consent append-only để có lịch sử phục vụ DPIA. "Đồng ý chia sẻ với một người thân cụ thể" là `caregiver_links.sharing_enabled` của đúng dòng link đó, không phải một dòng `user_consents` riêng — vì consent là theo mục đích xử lý (purpose), còn công tắc chia sẻ là theo từng mối liên kết.
6. **Offline**: `dose_logs.client_uuid` đảm bảo đồng bộ lặp lại không tạo bản ghi trùng; `UNIQUE(medication_schedule_id, scheduled_at)` đảm bảo Worker và API không cùng ghi 2 dòng cho một lượt uống.
7. Các cột hành chính (số giấy phép lưu hành, ngày hết hạn, tuổi thọ sản phẩm, trạng thái lưu hành) đã loại khỏi `medications` vì không phục vụ nhắc thuốc hay cảnh báo tương tác trong scope hiện tại.
8. Đã bỏ tính năng AI hỏi đáp: không có bảng `ai_conversations`/`ai_messages`. Không bảng nào dùng pgvector; nếu không có kế hoạch dùng trong Phase 1 thì bỏ khỏi §10 của Proposal hoặc ghi "reserved for Phase 2".
9. **Xóa mềm danh mục**: `medications`, `active_ingredient_interactions`, `drug_food_interactions` dùng `deleted_at`. Truy vấn ứng dụng luôn lọc `deleted_at IS NULL`; bản ghi có tham chiếu lịch sử không bị xóa cứng.
10. **Nhật ký đồng bộ**: mỗi lượt chạy job đồng bộ danh mục (PB06) tạo một dòng `catalog_sync_runs`, phục vụ màn lịch sử đồng bộ trên Admin Dashboard và AC "sync log stored with timestamp + record count".
11. **Không có nhập thuốc tự do** (từ v5): Admin bổ sung đủ thuốc cần dùng vào danh mục.
12. **Simple Mode là cài đặt cục bộ, không phải dữ liệu server**: lưu bằng `SharedPreferences` (Android) / `UserDefaults` (iOS), không qua Backend API, không có bảng nào chứa nó. AC của PB33/6.04 ("persists across sessions") đạt bằng lưu cục bộ, chỉ trong phạm vi cùng một thiết bị.
13. **Thuốc chưa map hoạt chất hiển thị riêng khi tra tương tác**: `InteractionEvaluator` liệt kê nhóm `has_interaction_data = false` riêng biệt, không gộp với nhóm "đã kiểm tra, không thấy tương tác" — giữ nguyên tắc 3 trạng thái (FR04, CD7).
14. **[SỬA] Không có Apple Developer Program trong Phase 1**: push FCM không tới máy iOS vì không có APNs. Quyết định: người thân dùng iOS nhận cảnh báo bằng cách app kéo danh sách cảnh báo khi mở hoặc vào foreground (C4 spec DM3); Worker bỏ qua token `ios` khi gửi push. Đây là giới hạn đã biết, cần ghi vào risk register.
15. **[MỚI] Trạng thái Worker nằm trong DB**: con trỏ quét, heartbeat, `dedupe_key` và trạng thái yêu cầu xóa đều lưu ở Postgres. Redis chỉ là hàng đợi không bền vững; mất dữ liệu Redis không làm mất trạng thái (CD6, CD10).
16. **[MỚI] Nhóm bệnh là dữ liệu**: `disease_groups` là bảng lookup, nên thêm nhóm ở Phase 2 chỉ là thêm dòng cộng cấu hình (QA.10).

---

## Phụ lục A — Bảng mới và cột thay đổi ở v9

| Bảng | Thay đổi |
|---|---|
| `disease_groups` | **Bảng mới** |
| `missed_dose_scan_cursor` | **Bảng mới** |
| `worker_heartbeats` | **Bảng mới** |
| `active_ingredients` | Xóa `disease_group` |
| `active_ingredient_disease_groups` | `disease_group` (ENUM) → `disease_group_id` (FK); thêm UNIQUE |
| `catalog_sync_runs` | Làm rõ quy tắc cập nhật (không đổi cột) |
| `users` | Thêm `erased_at`; `full_name`, `date_of_birth`, `gender` nullable; sửa/thêm CHECK |
| `data_deletion_requests` | Xóa `request_type`, `consent_type`; thêm `completed_at`, `last_error`; thêm CHECK, partial unique index, index |
| `access_logs` | Thêm index `(actor_user_id, accessed_at)` |
| `medication_schedules` | Thêm `effective_from` |
| `dose_logs` | Làm rõ `client_uuid`, `taken_at` nullable |
| `notifications` | Thêm `dedupe_key`, `created_at`; thêm index |

---

## Phụ lục B — Bảng đối chiếu tên cũ → tên mới (v7 → v8)

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
