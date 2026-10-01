# DrugTime — Schema Cơ Sở Dữ Liệu (Bản Chốt v6)

Ký hiệu thay đổi: **[MỚI]** = bảng/cột mới, **[SỬA]** = bảng/cột đã chỉnh, **[XÓA]** = đã loại bỏ. Ký hiệu trong bảng áp dụng cho thay đổi **gần nhất tính đến v6**; các thay đổi cũ hơn giữ nguyên như tài liệu gốc và không đánh dấu lại.

## Lịch sử thay đổi

### v2 → v3
Phát sinh từ việc rà soát Sprint Backlog đối chiếu với Schema v2 (xem `DrugTime_Sprint_Backlog_Task_Descriptions.md`, mục 0):

1. **Xóa mềm cho danh mục** — PB04/PB05 yêu cầu xóa mềm nhưng `medications`, `active_ingredient_interactions`, `drug_food_interactions` chưa có cột đánh dấu. → thêm `deleted_at` (nullable) cho cả 3 bảng.
2. **Nhật ký đồng bộ danh mục** — PB06 yêu cầu "sync log with timestamp + record count" nhưng chưa có bảng lưu. → thêm bảng `catalog_sync_runs`.
3. **Chống trùng lượt uống** — job phát hiện bỏ lỡ (PB20) và API xác nhận liều (PB13) có thể cùng ghi vào `dose_logs` cho cùng một lượt nếu chạy gần nhau. → thêm `UNIQUE(medication_schedule_id, thoi_gian_du_kien)` trên `dose_logs`.
4. ~~Thuốc ngoài danh mục: thêm `ten_tu_nhap` tự do~~ — sửa ở v3 → v4, rồi **bỏ hẳn ở v4 → v5** (xem bên dưới).
5. **Simple Mode không cần lưu server** — `users.che_do_nguoi_cao_tuoi` là tùy chọn giao diện của thiết bị đang dùng, không phải dữ liệu cần chia sẻ hay đồng bộ. → bỏ cột, chuyển sang lưu cục bộ trên máy (`SharedPreferences`/`UserDefaults`).

### v3 → v4

1. **Đăng nhập bằng email hoặc SĐT** — PB01 cho phép cả hai. → thêm `users.email` (nullable, UNIQUE), ràng buộc phải có ít nhất một trong email/SĐT.
2. ~~Thuốc ngoài danh mục — chống trùng lặp bằng bảng gom nhóm `free_text_medication_names`~~ — **bỏ hẳn ở v4 → v5**, xem bên dưới.
3. **Xác nhận không mua Apple Developer Program (trả phí)** — team dùng Apple ID miễn phí cho toàn bộ Phase 1. Không đổi cấu trúc bảng, nhưng ghi nhận hệ quả ở ghi chú §14: build iOS chỉ cài được qua Xcode trực tiếp (không TestFlight/Ad Hoc), và **FCM push không hoạt động trên iOS** vì thiếu APNs — ảnh hưởng trực tiếp tới PB20 (cảnh báo bỏ lỡ liều cho người thân dùng iOS).

### v4 → v5

1. **Bỏ hẳn việc nhập tự do cho thuốc** — quyết định mới: Admin sẽ chủ động bổ sung đủ thuốc cần dùng vào danh mục (`medications`) thay vì để patient tự gõ tên khi không khớp. → bỏ bảng `free_text_medication_names`; `user_medications.medication_id` trở lại **bắt buộc** (NOT NULL), bỏ cột `ten_tu_nhap` và `free_text_medication_id`.
2. **Kết quả tra tương tác khi thiếu dữ liệu**: giữ nguyên nguyên tắc 3 trạng thái (có tương tác / đã kiểm tra không thấy / không đủ dữ liệu). Trạng thái "không đủ dữ liệu" giờ chỉ xảy ra khi thuốc **có trong danh mục nhưng chưa được Admin gán hoạt chất** — không còn phát sinh từ việc người dùng gõ tên tự do, vì đường đó không còn tồn tại.

Không có thay đổi phá vỡ tương thích ngược ở vòng này ngoài việc siết `medication_id` về NOT NULL — cần đảm bảo dữ liệu hiện có (nếu đã có dòng NULL từ v3/v4) được gán lại trước khi migrate.

### v5 → v6 (bản này)

1. **Bỏ `unmatched_scan_logs` cho đơn giản** — bảng ghi lại chuỗi ML Kit không khớp danh mục bị loại bỏ. → bỏ bảng. Hệ quả: task **4.11 (Log unmatched items for Admin catalog review, PB31)** trong Sprint Backlog mất phần dữ liệu để dựa vào — Admin không còn nguồn tự động cho biết thuốc nào bị quét hụt nhiều lần để ưu tiên bổ sung; phải dựa vào phản hồi thủ công từ người dùng hoặc theo dõi qua kênh khác. R-01 (rủi ro quét không khớp) vẫn được giảm nhẹ bằng fallback tìm thủ công (3.05), chỉ mất phần "biết để bổ sung danh mục".

---

## Nhóm 1 — Danh mục thuốc

### `medications` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `ten_thuoc` | |
| `hoat_chat_raw` | Text thô từ nguồn dữ liệu gốc, dùng để đối chiếu khi mapping |
| `ham_luong` | Text gốc, dùng để hiển thị |
| `dang_bao_che` | |
| `cty_san_xuat_ten` | |
| `cty_san_xuat_nuoc` | |
| `quy_cach_dong_goi` | |
| `deleted_at` | **[MỚI]** nullable — xóa mềm; NULL = đang lưu hành trong ứng dụng |

> Mọi truy vấn của Mobile/Admin (trừ màn quản trị "xem đã xóa") phải lọc `deleted_at IS NULL`. Bản ghi có `deleted_at` khác NULL vẫn được `medication_active_ingredients`, `user_medications` tham chiếu để giữ lịch sử — không xóa cứng khi còn tham chiếu.

### `active_ingredients` (Bảng A)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `ten_hoat_chat_chuan` | |
| `vai_tro` | ENUM: `dieu_tri_benh_nen` / `trieu_chung_cap_tinh` |
| `nhom_benh` | FK nullable |
| `nhom_duoc_ly` | |
| `atc_code` | |
| `nguon` | |

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
| `ham_luong_value` | Số, vd `500` |
| `ham_luong_unit` | vd `"mg"`, `"mcg"`, `"mg/5ml"` |
| `don_vi_dinh_luong` | vd `"viên"`, `"ml"`, `"gói"` |

Cho phép 1 thuốc có nhiều hoạt chất (thuốc phối hợp) với hàm lượng có cấu trúc, phục vụ tính tổng liều/ngày.

### `active_ingredient_nhom_benh`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `active_ingredient_id` | FK |
| `nhom_benh` | ENUM |

### `catalog_sync_runs` **[MỚI]**
Phục vụ PB06 (nhật ký đồng bộ danh mục từ Nguồn dữ liệu quản lý dược Việt Nam).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `nguon` | ENUM: `dav_drugbank` / `qd_5948` / `duoc_thu_qg` — nguồn nào được đồng bộ |
| `bat_dau_luc` | |
| `ket_thuc_luc` | nullable — NULL nếu job đang chạy hoặc bị treo |
| `trang_thai` | ENUM: `dang_chay` / `thanh_cong` / `that_bai` |
| `so_ban_ghi_them` | mặc định 0 |
| `so_ban_ghi_cap_nhat` | mặc định 0 |
| `so_ban_ghi_loi` | mặc định 0 |
| `chi_tiet_loi` | nullable — text/JSON tóm tắt các bản ghi lỗi (không lưu toàn bộ payload) |
| `kich_hoat_boi` | ENUM: `scheduler` / `admin_thu_cong` |

> Index: `(nguon, bat_dau_luc DESC)` cho màn lịch sử đồng bộ trên Admin Dashboard. Append-only — job không tự sửa dòng cũ, chỉ tạo dòng mới mỗi lần chạy.

---

## Nhóm 3 — Tri thức dược

### `conditions` (Bảng B)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `ten` | |
| `ban_chat_y_khoa` | `benh_ly` / `sinh_ly_binh_thuong` |
| `vai_tro_du_lieu` | `sinh_hoat_chat_dieu_tri` / `dieu_chinh_thuoc_khac` |
| `icd10_code` | optional |

### `active_ingredient_interactions` (Bảng C) **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `hoat_chat_a_id` | FK bắt buộc |
| `hoat_chat_b_id` | FK nullable |
| `hoat_chat_b_ten_ngoai` | nullable |
| `hoat_chat_b_trong_bang_a` | `co` / `khong` |
| `loai_tuong_tac` | ENUM: `chong_chi_dinh` (tuyệt đối, không xét liều) / `phu_thuoc_lieu` (mức độ thay đổi theo tổng liều/ngày) |
| `muc_do` | 1–4 |
| `loai_xu_ly` | `tranh_phoi_hop` / `can_theo_doi` / `cach_gio` / `giam_lieu` |
| `khoang_cach_toi_thieu_gio` | nullable |
| `mo_ta` | |
| `nguon` | |
| `trang_thai_xac_minh` | |
| `deleted_at` | **[MỚI]** nullable — xóa mềm |

> Khi `loai_tuong_tac = 'chong_chi_dinh'`: dùng trực tiếp `muc_do` và `mo_ta` của dòng này, **không cần** tính liều hay tra bảng ngưỡng.
> Khi `loai_tuong_tac = 'phu_thuoc_lieu'`: tính tổng liều/ngày rồi tra `active_ingredient_interaction_dose_thresholds`.
> Việc kiểm tra tương tác là **xác định (rule-based)** trên các bảng này; LLM không tham gia (QA.04).
> `InteractionEvaluator` chỉ đọc các dòng `deleted_at IS NULL`.

### `active_ingredient_interaction_dose_thresholds`
*(chỉ áp dụng khi `active_ingredient_interactions.loai_tuong_tac = 'phu_thuoc_lieu'`)*

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `interaction_id` | FK → `active_ingredient_interactions.id` |
| `ingredient_ref` | `'A'` hoặc `'B'` — ngưỡng áp dụng cho hoạt chất nào trong cặp |
| `lieu_toi_thieu` | nullable |
| `lieu_toi_da` | nullable |
| `don_vi_lieu` | vd `"mg/ngày"` |
| `muc_do` | Ghi đè `muc_do` của bảng C theo ngưỡng liều thực tế |
| `canh_bao_text` | |

### `drug_food_interactions` (Bảng D) **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `hoat_chat_id` | FK |
| `thuc_pham_can_tranh` | |
| `muc_do` | |
| `ly_do` | |
| `nguon` | |
| `trang_thai_xac_minh` | |
| `deleted_at` | **[MỚI]** nullable — xóa mềm |

### `active_ingredient_precautions` (Bảng E)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `hoat_chat_id` | FK |
| `dieu_kien_id` | FK → `conditions.id` |
| `muc_do` | kèm Chống chỉ định |
| `mo_ta_dieu_chinh` | |
| `nguon` | |
| `trang_thai_xac_minh` | |

### `drug_classes` (Bảng F)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `ten_nhom` | |
| `nguon` | |

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
| `ho_ten` | |
| `ngay_sinh` | |
| `gioi_tinh` | |
| `so_dien_thoai` | nullable, UNIQUE — dùng để đăng nhập bằng SĐT |
| `email` | **[MỚI]** nullable, UNIQUE — dùng để đăng nhập bằng email |
| ~~`che_do_nguoi_cao_tuoi`~~ | **[XÓA]** Simple Mode chuyển sang lưu cục bộ trên thiết bị (xem ghi chú §12) |
| `vai_tro_he_thong` | ENUM: `user` / `admin`, mặc định `user`. Chỉ dùng để cấp quyền vào Admin Dashboard |

> Ràng buộc: **[MỚI]** `CHECK (email IS NOT NULL OR so_dien_thoai IS NOT NULL)` — bắt buộc có ít nhất một phương thức đăng nhập. Supabase Auth (`auth.users`) đã có sẵn email/phone dùng để xác thực; cột ở đây là bản sao phục vụ hiển thị/tìm kiếm trong `public.users` mà không phải gọi API admin của Auth.

### `user_consents`
Append-only: mỗi lần đồng ý là một dòng mới; rút consent cập nhật `thoi_gian_thu_hoi` và `trang_thai`, không xóa dòng. Consent thuộc về **data subject** (patient): khi A giám sát B, consent `family_sharing` nằm ở dòng của B.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — chủ thể dữ liệu |
| `loai_dong_y` | ENUM theo mục đích: `health_data` / `family_sharing` / `ai_meal` (mở rộng khi thêm purpose Phase 2) |
| `trang_thai` | ENUM: `dong_y` / `thu_hoi` |
| `thoi_gian_dong_y` | |
| `thoi_gian_thu_hoi` | nullable |
| `phien_ban_van_ban` | phiên bản văn bản consent đã hiển thị |

> Ràng buộc: tối đa 1 dòng `trang_thai = 'dong_y'` cho mỗi `(user_id, loai_dong_y)` (partial unique index).

### `data_deletion_requests`
Phục vụ QA.01, FR09.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `loai` | ENUM: `xoa_du_lieu` / `rut_consent` |
| `loai_dong_y` | nullable — purpose bị rút (khi `loai = 'rut_consent'`) |
| `trang_thai` | ENUM: `cho_duyet` / `da_duyet` / `tu_choi` / `hoan_tat` |
| `thoi_gian_yeu_cau` | |
| `admin_xu_ly_id` | FK → `users.id`, nullable |
| `thoi_gian_xu_ly` | nullable |
| `ly_do_tu_choi` | nullable |

### `caregiver_links`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `patient_user_id` | FK → `users.id` |
| `family_user_id` | FK → `users.id` |
| `trang_thai` | ENUM: `pending` / `active` / `revoked` |
| `cho_phep_chia_se` | boolean — công tắc chia sẻ do patient điều khiển |
| `thoi_gian_lien_ket` | |
| `thoi_gian_thu_hoi` | nullable |

> Ràng buộc: `UNIQUE(patient_user_id, family_user_id)`; `CHECK(patient_user_id <> family_user_id)`.
> Index: `(family_user_id, trang_thai)` cho màn hình "Người thân của tôi"; `(patient_user_id, trang_thai)` cho Worker khi tìm người nhận cảnh báo.
> Quan hệ không đối xứng: A giám sát B không cấp quyền nào cho B trên dữ liệu của A.

### `link_codes`
Mã QR / referral do patient tạo để mời người thân (FR07).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `patient_user_id` | FK |
| `ma` | UNIQUE |
| `het_han_luc` | |
| `da_dung` | boolean |
| `family_user_id` | FK nullable — người đã dùng mã |

### `device_tokens`
Token FCM để Worker gửi cảnh báo bỏ lỡ liều.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `fcm_token` | UNIQUE |
| `platform` | ENUM: `android` / `ios` |
| `cap_nhat_luc` | |

### `access_logs`
Append-only. Phục vụ NFR06, QA.02, QA.09.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `actor_user_id` | FK → `users.id` |
| `actor_role` | ENUM: `self` / `family` / `admin` — **tính theo từng lần truy cập** từ quan hệ actor–patient, không đọc từ `users` |
| `patient_user_id` | FK → `users.id` |
| `data_scope` | ENUM: `ho_so_suc_khoe` / `danh_sach_thuoc` / `lich_su_tuan_thu` / `canh_bao_tuong_tac` / `goi_y_bua_an` |
| `ket_qua` | ENUM: `allowed` / `denied` |
| `ly_do_tu_choi` | nullable |
| `thoi_gian` | |

> Index: `(patient_user_id, thoi_gian)`. Không cấp quyền UPDATE/DELETE cho role ứng dụng.

### `dpia_records`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `ten_luong_du_lieu` | vd `"Gửi điều kiện bệnh nền cho LLM (meal suggestion)"` |
| `co_chuyen_du_lieu_xuyen_bien_gioi` | boolean |
| `trang_thai` | ENUM: `ban_nhap` / `dang_xem_xet` / `da_phe_duyet` |
| `nguoi_phe_duyet_id` | FK → `users.id`, nullable |
| `ngay_phe_duyet` | nullable |

---

## Nhóm 5 — Hồ sơ y tế & lịch uống thuốc

### `user_conditions`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `condition_id` | FK |
| `subtype` | nullable — chỉ dùng cho Tiểu đường |
| `phan_do` | nullable — chỉ dùng cho Suy thận mạn |

### `don_thuoc`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `nguon_nhap` | `ocr_scan` / `thu_cong` / `mac_dinh` |
| `ngay_ke_don` | nullable |
| `noi_ke_don` | nullable |
| `trang_thai` | `dang_dung` / `da_ket_thuc` — chỉ `dang_dung` được đưa vào phân tích tương tác |

### `user_medications` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `don_thuoc_id` | FK bắt buộc, không NULL |
| `medication_id` | FK bắt buộc, không NULL — patient chỉ chọn thuốc có sẵn trong danh mục, không nhập tự do |
| `cach_nhap` | `thu_cong` / `ocr_scan` (quét blister on-device bằng ML Kit) |
| `trang_thai_xac_nhan` | |
| `so_luong_moi_lan` | Số — vd số viên/ml mỗi lần uống |
| `so_lan_moi_ngay` | Số — tần suất/ngày |
| `co_du_lieu_tuong_tac` | boolean — `false` khi thuốc có trong danh mục nhưng Admin chưa map hoạt chất (dữ liệu danh mục chưa đầy đủ); không còn liên quan tới việc nhập tự do vì trường hợp đó không tồn tại nữa |

> Cả quét vỉ (PB31) lẫn nhập tay (PB10) đều chỉ tạo được dòng khi đã chọn một `medications` cụ thể qua tìm kiếm/gợi ý. Quét không khớp → chuyển sang tìm thủ công (3.05); tìm thủ công không ra → không thêm được thuốc đó vào lịch. Đây là giới hạn Phase 1 đã biết, đổi lại tránh được toàn bộ vấn đề trùng lặp/biến thể chính tả của việc cho nhập tự do.
> `so_luong_moi_lan × so_lan_moi_ngay × ham_luong_value` (từ `medication_active_ingredients`) = tổng liều/ngày dùng để tra `active_ingredient_interaction_dose_thresholds`.
> Khi tra tương tác: thuốc có `co_du_lieu_tuong_tac = false` (chưa map hoạt chất) được liệt kê riêng cho người dùng biết "thuốc này chưa có dữ liệu để kiểm tra tương tác", tách khỏi các thuốc đã kiểm tra được — không gộp chung với kết quả "không có tương tác" (QA.04, xem PB24).

### `medication_schedules`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_medication_id` | FK |
| `gio_uong` | Phục vụ nhắc lịch, **không** dùng trong tính tương tác |
| `ngay_trong_tuan` | |
| `bat_tat_nhac` | |

### `dose_logs` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `medication_schedule_id` | FK |
| `thoi_gian_du_kien` | |
| `thoi_gian_thuc_uong` | |
| `trang_thai` | `Đã uống` / `Bỏ lỡ` / `Uống trễ` |
| `client_uuid` | UNIQUE — khóa idempotent do app sinh, chống ghi trùng khi đồng bộ sau offline (QA.08) |
| `dong_bo_luc` | nullable — thời điểm bản ghi được đồng bộ lên server |

> Ràng buộc: **[MỚI]** `UNIQUE(medication_schedule_id, thoi_gian_du_kien)` — mỗi lượt uống (một `medication_schedule_id` tại một `thoi_gian_du_kien` cụ thể) chỉ có đúng 1 bản ghi. Chống việc Worker (job phát hiện bỏ lỡ, PB20) và Backend (API xác nhận liều, PB13) cùng ghi 2 dòng cho cùng một lượt khi chạy gần nhau.
> Quy tắc ghi khi có xung đột: dùng `INSERT ... ON CONFLICT (medication_schedule_id, thoi_gian_du_kien) DO UPDATE` — nếu dòng đã tồn tại với `trang_thai = 'Bỏ lỡ'` và request xác nhận đến sau đó, cập nhật thành `Uống trễ` cùng `thoi_gian_thuc_uong`; nếu dòng đã có `thoi_gian_thuc_uong` (đã xác nhận), job phát hiện bỏ lỡ **không được ghi đè**. `client_uuid` vẫn giữ vai trò chống gửi trùng từ chính Outbox của Mobile.

### `notifications`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — người nhận |
| `ve_patient_user_id` | FK → `users.id` — thông báo nói về patient nào (= `user_id` nếu là nhắc của chính mình) |
| `loai` | ENUM: `nhac_uong_thuoc` / `canh_bao_bo_lo_lieu_nguoi_than` |
| `noi_dung` | |
| `da_doc` | |

### `meal_suggestions`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — patient được gợi ý |
| `noi_dung_goi_y` | |
| `dua_tren_dieu_kien` | FK nullable |

---

## Nhóm 6 — Tầng tổng hợp

### `regimen_analysis_snapshots`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `thoi_gian_phan_tich` | |

### `regimen_analysis_findings`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `snapshot_id` | FK |
| `loai_canh_bao` | |
| `nguon_bang` | ENUM: `interactions` / `drug_food` / `precautions` / `drug_classes` — bảng nguồn của cảnh báo |
| `nguon_id` | id bản ghi trong bảng nguồn |
| `hien_thi_cho_nguoi_dung` | |

### `regimen_analysis_finding_medications`
Thay cho cột "FK nhiều" `don_thuoc_lien_quan`.

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
| `da_xem` | |
| `da_xu_ly` | |

---

## Nhóm 7 — Kiểm thử

### `kich_ban_benh_nhan_mau` (Bảng G)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `ten_kich_ban` | |
| `ket_qua_ky_vong` | |
| `danh_gia_duoc_si` | |

### `kich_ban_dieu_kien`
| Cột | Ghi chú |
|---|---|
| `kich_ban_id` | FK |
| `dieu_kien_id` | FK |

### `kich_ban_hoat_chat`
| Cột | Ghi chú |
|---|---|
| `kich_ban_id` | FK |
| `hoat_chat_id` | FK |

---

## Quy tắc phân quyền (Backend API)

```
Request của caller C lên dữ liệu của patient P:
  C = P                                   → actor_role = self    (cần consent purpose tương ứng của P)
  tồn tại link(P, C) trang_thai = active
    và cho_phep_chia_se = true
    và consent family_sharing của P còn hiệu lực
                                          → actor_role = family
  C.vai_tro_he_thong = admin              → actor_role = admin   (ghi log bắt buộc)
  còn lại                                 → 403 + ghi ket_qua = denied vào access_logs
```

Mobile App và Admin Web **chỉ gọi Backend API**; chỉ API và Worker truy cập Supabase (bật RLS, không policy cho `anon`/`authenticated`).

---

## Ghi chú thiết kế quan trọng

1. **Chống chỉ định vs. phụ thuộc liều**: `active_ingredient_interactions.loai_tuong_tac` tách 2 loại. Chống chỉ định là cảnh báo tuyệt đối, không xét liều; phụ thuộc liều cần tính tổng liều/ngày và tra bảng ngưỡng riêng.
2. **Tính tổng liều/ngày**: dựa trên tần suất uống thực tế (`so_luong_moi_lan × so_lan_moi_ngay`) nhân hàm lượng mỗi đơn vị (`medication_active_ingredients.ham_luong_value`), không phải hàm lượng ghi trên nhãn.
3. **`gio_uong`** chỉ phục vụ nhắc lịch, tách hoàn toàn khỏi logic kiểm tra tương tác.
4. **Vai trò theo ngữ cảnh**: không lưu Patient/Family Member trên `users`; suy ra từ `caregiver_links` tại thời điểm truy cập và ghi vào `access_logs.actor_role`.
5. **Consent theo chủ thể dữ liệu**: consent `family_sharing` do patient cấp; consent append-only để có lịch sử phục vụ DPIA. "Đồng ý chia sẻ với một người thân cụ thể" là `caregiver_links.cho_phep_chia_se` của đúng dòng link đó, không phải một dòng `user_consents` riêng — vì consent là theo mục đích xử lý (purpose), còn công tắc chia sẻ là theo từng mối liên kết.
6. **Offline**: `dose_logs.client_uuid` đảm bảo đồng bộ lặp lại không tạo bản ghi trùng; `UNIQUE(medication_schedule_id, thoi_gian_du_kien)` **[MỚI]** đảm bảo Worker và API không cùng ghi 2 dòng cho một lượt uống.
7. Các cột hành chính (số giấy phép lưu hành, ngày hết hạn, tuổi thọ sản phẩm, trạng thái lưu hành) đã loại khỏi `medications` vì không phục vụ nhắc thuốc hay cảnh báo tương tác trong scope hiện tại.
8. Đã bỏ tính năng AI hỏi đáp: không có bảng `ai_conversations`/`ai_messages`. Không bảng nào dùng pgvector; nếu không có kế hoạch dùng trong Phase 1 thì bỏ khỏi §10 hoặc ghi "reserved for Phase 2".
9. **[MỚI] Xóa mềm danh mục**: `medications`, `active_ingredient_interactions`, `drug_food_interactions` dùng `deleted_at` (nullable). Truy vấn ứng dụng luôn lọc `deleted_at IS NULL`; bản ghi có tham chiếu lịch sử (`user_medications`, `regimen_analysis_findings`...) không bao giờ bị xóa cứng, chỉ đánh dấu xóa mềm.
10. **[MỚI] Nhật ký đồng bộ**: mỗi lượt chạy job đồng bộ danh mục (PB06) tạo một dòng `catalog_sync_runs` (append-only), phục vụ màn lịch sử đồng bộ trên Admin Dashboard và AC "sync log stored with timestamp + record count".
11. ~~Thuốc ngoài danh mục: `medication_id` NULL + `ten_tu_nhap`~~ — **đã bỏ ở v4 → v5**: PB04 sẽ được Admin bổ sung đủ thuốc cần dùng, không cần đường nhập tự do cho patient.
12. **[MỚI] Simple Mode là cài đặt cục bộ, không phải dữ liệu server**: bật/tắt lưu bằng `SharedPreferences` (Android) / `UserDefaults` (iOS) ngay trên máy, không qua Backend API, không có bảng nào chứa nó. Lý do: đây là tùy chọn giao diện của người đang cầm máy tại thời điểm đó, không phải thuộc tính của tài khoản hay của patient — lưu ở server sẽ khiến cài đặt "đi theo" tài khoản sang cả những thiết bị/người dùng khác không mong muốn. Hệ quả cho Sprint Backlog: AC của PB33/6.04 ("persists across sessions") vẫn đạt bằng lưu cục bộ; phần "giữ nguyên khi đăng nhập lại" chỉ áp dụng trong phạm vi cùng một thiết bị, không đồng bộ khi đổi máy.
13. **[MỚI] Thuốc không map được hoạt chất vẫn hiển thị riêng khi tra tương tác**: dù `user_medications.medication_id` giờ luôn trỏ tới danh mục, một thuốc trong danh mục vẫn có thể chưa được Admin gán hoạt chất (`co_du_lieu_tuong_tac = false`, dữ liệu danh mục chưa đầy đủ). `InteractionEvaluator` phải liệt kê rõ nhóm thuốc này riêng biệt (kèm thông báo "chưa có dữ liệu để kiểm tra"), không gộp chung với nhóm "đã kiểm tra, không thấy tương tác" — giữ đúng nguyên tắc 3 trạng thái của QA.04.
14. **[MỚI] Không có Apple Developer Program trong Phase 1**: hệ quả không nằm ở cấu trúc bảng mà ở tầng vận hành — `device_tokens.platform='ios'` vẫn hợp lệ về mặt dữ liệu (app vẫn xin được token FCM), nhưng Backend/Worker cần biết là gửi push tới token này **sẽ không tới máy** vì APNs chưa được cấu hình (cần tài khoản trả phí). Team cần quyết định một trong hai hướng cho PB20 trên iOS: (a) chấp nhận đây là giới hạn đã biết của Phase 1 và ghi vào tài liệu bàn giao/risk register, người thân dùng iOS chỉ thấy cảnh báo khi tự mở app; hoặc (b) bổ sung task cho Mobile tự động làm mới (poll) danh sách cảnh báo mỗi khi app mở lên/vào foreground, để giảm bớt ảnh hưởng dù không real-time.
