# DrugTime — Schema Cơ Sở Dữ Liệu (Bản Chốt v2)

Capstone Project 1 (C1SE.07), International School, Đại học Duy Tân.

Ký hiệu thay đổi so với v1: **[MỚI]** = bảng/cột mới, **[SỬA]** = bảng/cột đã chỉnh, **[XÓA]** = đã loại bỏ.

---

## Nhóm 1 — Danh mục thuốc

### `medications`
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

### `active_ingredient_interactions` (Bảng C)
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

> Khi `loai_tuong_tac = 'chong_chi_dinh'`: dùng trực tiếp `muc_do` và `mo_ta` của dòng này, **không cần** tính liều hay tra bảng ngưỡng.
> Khi `loai_tuong_tac = 'phu_thuoc_lieu'`: tính tổng liều/ngày rồi tra `active_ingredient_interaction_dose_thresholds`.
> Việc kiểm tra tương tác là **xác định (rule-based)** trên các bảng này; LLM không tham gia (QA.04).

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

### `drug_food_interactions` (Bảng D)
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `hoat_chat_id` | FK |
| `thuc_pham_can_tranh` | |
| `muc_do` | |
| `ly_do` | |
| `nguon` | |
| `trang_thai_xac_minh` | |

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
| `so_dien_thoai` | |
| `che_do_nguoi_cao_tuoi` | Simple Mode — tùy chọn giao diện của người đang dùng máy, không gắn với patient đang xem |
| `vai_tro_he_thong` | **[MỚI]** ENUM: `user` / `admin`, mặc định `user`. Chỉ dùng để cấp quyền vào Admin Dashboard |
| ~~`vai_tro`~~ | **[XÓA]** (`Patient` / `Family Member`) — thay bằng quan hệ trong `caregiver_links` |

### `user_consents` **[SỬA]**
Append-only: mỗi lần đồng ý là một dòng mới; rút consent cập nhật `thoi_gian_thu_hoi` và `trang_thai`, không xóa dòng. Consent thuộc về **data subject** (patient): khi A giám sát B, consent `family_sharing` nằm ở dòng của B.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — chủ thể dữ liệu |
| `loai_dong_y` | ENUM theo mục đích: `health_data` / `family_sharing` / `ai_meal` (mở rộng khi thêm purpose Phase 2) |
| `trang_thai` | ENUM: `dong_y` / `thu_hoi` |
| `thoi_gian_dong_y` | |
| `thoi_gian_thu_hoi` | **[MỚI]** nullable |
| `phien_ban_van_ban` | **[MỚI]** phiên bản văn bản consent đã hiển thị |

> Ràng buộc: tối đa 1 dòng `trang_thai = 'dong_y'` cho mỗi `(user_id, loai_dong_y)` (partial unique index).

### `data_deletion_requests` **[MỚI]**
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

### `caregiver_links` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `patient_user_id` | FK → `users.id` |
| `family_user_id` | FK → `users.id` |
| `trang_thai` | ENUM: `pending` / `active` / `revoked` |
| `cho_phep_chia_se` | **[MỚI]** boolean — công tắc chia sẻ do patient điều khiển |
| `thoi_gian_lien_ket` | **[MỚI]** |
| `thoi_gian_thu_hoi` | **[MỚI]** nullable |

> Ràng buộc: `UNIQUE(patient_user_id, family_user_id)`; `CHECK(patient_user_id <> family_user_id)`.
> Index: `(family_user_id, trang_thai)` cho màn hình "Người thân của tôi"; `(patient_user_id, trang_thai)` cho Worker khi tìm người nhận cảnh báo.
> Quan hệ không đối xứng: A giám sát B không cấp quyền nào cho B trên dữ liệu của A.

### `link_codes` **[MỚI]**
Mã QR / referral do patient tạo để mời người thân (FR07).

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `patient_user_id` | FK |
| `ma` | UNIQUE |
| `het_han_luc` | |
| `da_dung` | boolean |
| `family_user_id` | FK nullable — người đã dùng mã |

### `device_tokens` **[MỚI]**
Token FCM để Worker gửi cảnh báo bỏ lỡ liều.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `fcm_token` | UNIQUE |
| `platform` | ENUM: `android` / `ios` |
| `cap_nhat_luc` | |

### `access_logs` **[MỚI]**
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

### `dpia_records` **[MỚI]**
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

### `user_medications`
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `don_thuoc_id` | FK bắt buộc, không NULL |
| `medication_id` | FK nullable |
| `cach_nhap` | `thu_cong` / `ocr_scan` (quét blister on-device bằng ML Kit) |
| `trang_thai_xac_nhan` | |
| `so_luong_moi_lan` | Số — vd số viên/ml mỗi lần uống |
| `so_lan_moi_ngay` | Số — tần suất/ngày |
| `co_du_lieu_tuong_tac` | boolean |

> `so_luong_moi_lan × so_lan_moi_ngay × ham_luong_value` (từ `medication_active_ingredients`) = tổng liều/ngày dùng để tra `active_ingredient_interaction_dose_thresholds`.

### `unmatched_scan_logs` **[MỚI]**
Chuỗi ML Kit nhận diện nhưng không khớp danh mục (R-01), để Admin xem xét khi đồng bộ danh mục. Không lưu ảnh.

| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK |
| `chuoi_nhan_dien` | |
| `thoi_gian` | |
| `admin_da_xem_xet` | boolean |

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
| `client_uuid` | **[MỚI]** UNIQUE — khóa idempotent do app sinh, chống ghi trùng khi đồng bộ sau offline (QA.08) |
| `dong_bo_luc` | **[MỚI]** nullable — thời điểm bản ghi được đồng bộ lên server |

### `notifications` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `user_id` | FK — người nhận |
| `ve_patient_user_id` | **[MỚI]** FK → `users.id` — thông báo nói về patient nào (= `user_id` nếu là nhắc của chính mình) |
| `loai` | **[SỬA]** ENUM: `nhac_uong_thuoc` / `canh_bao_bo_lo_lieu_nguoi_than` |
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

### `regimen_analysis_findings` **[SỬA]**
| Cột | Ghi chú |
|---|---|
| `id` | PK |
| `snapshot_id` | FK |
| `loai_canh_bao` | |
| `nguon_bang` | **[SỬA]** ENUM: `interactions` / `drug_food` / `precautions` / `drug_classes` — bảng nguồn của cảnh báo |
| `nguon_id` | **[SỬA]** id bản ghi trong bảng nguồn (thay cho "FK linh hoạt") |
| `hien_thi_cho_nguoi_dung` | |

### `regimen_analysis_finding_medications` **[MỚI]**
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
5. **Consent theo chủ thể dữ liệu**: consent `family_sharing` do patient cấp; consent append-only để có lịch sử phục vụ DPIA.
6. **Offline**: `dose_logs.client_uuid` đảm bảo đồng bộ lặp lại không tạo bản ghi trùng.
7. Các cột hành chính (số giấy phép lưu hành, ngày hết hạn, tuổi thọ sản phẩm, trạng thái lưu hành) đã loại khỏi `medications` vì không phục vụ nhắc thuốc hay cảnh báo tương tác trong scope hiện tại.
8. Đã bỏ tính năng AI hỏi đáp: không có bảng `ai_conversations`/`ai_messages`. Không bảng nào dùng pgvector; nếu không có kế hoạch dùng trong Phase 1 thì bỏ khỏi §10 hoặc ghi "reserved for Phase 2".
