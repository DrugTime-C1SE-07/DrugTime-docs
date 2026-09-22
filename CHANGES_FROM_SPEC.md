# DrugTime — Thay Đổi Thiết Kế So Với Đặc Tả Gốc (CHANGES_FROM_SPEC.md)

Tài liệu này đối chiếu chi tiết **27 điểm thay đổi / bổ sung quan trọng** (gồm 12 điểm Vòng 1, 7 điểm Vòng 2, 5 điểm Vòng 3, và 3 điểm chốt hạ Vòng 4) so với tài liệu đặc tả ban đầu (`docs/drugtime_frontend_api_specification.md`).

---

## Bảng Tổng Hợp 27 Thay Đổi Cốt Lõi

| # | Hạng mục | Mức độ | Thay đổi so với bản gốc | Lý do kỹ thuật / Nghiệp vụ |
|---|---|---|---|---|
| **1** | **Chống Brute-force mã Caregiver** | Nghiêm trọng | Thêm Rate-limiter (tối đa 5 lần thử sai / 15 phút theo IP + caller). Trả mã lỗi riêng `LINK_CODE_RATE_LIMITED` (HTTP 429). | Mã 6 số có không gian 1.000.000 tổ hợp; nếu không rate-limit kẻ tấn công có thể dò mã để tự gắn quyền xem hồ sơ bệnh nhân. |
| **2** | **Phân quyền Đọc/Ghi cho `family`** | Nghiêm trọng | Bổ sung cờ `cho_phep_chinh_sua: boolean` trong `caregiver_links`. `verify_patient_access` nhận `required_permission: 'read' \| 'write'`. | Phân biệt người thân chỉ theo dõi (Read-only) vs người thân được phép kê thuốc/sửa lịch uống hộ người già (Write). |
| **3** | **Batch Sync trả kết quả Per-item** | Nghiêm trọng | `POST /dose-logs/batch-sync` trả mảng chi tiết từng liều: `{client_uuid, status: 'synced'\|'duplicate'\|'error', error_code?, message?}`. | Tránh mất âm thầm dữ liệu tuân thủ khi một vài item trong batch bị lỗi validate ở client offline. |
| **4** | **Tự động kích hoạt phân tích an toàn thuốc** | Nghiêm trọng | Bất kỳ thay đổi nào ở `user_medications` hoặc `user_conditions` đều tự động kích hoạt tiến trình phân tích an toàn (`regimen_analysis_snapshots`). | Tránh tình trạng Frontend quên gọi phân tích thủ công dẫn đến việc bệnh nhân dùng thuốc tương tác nguy hiểm mà không có cảnh báo. |
| **5** | **Phân trang Audit Log** | Trung bình | `GET /admin/audit-logs` thêm `page`, `page_size` theo chuẩn `PaginationEnvelope`. | Bảng `access_logs` là bảng lớn nhất và tăng trưởng nhanh nhất, bắt buộc phải phân trang (NFR06, QA.09). |
| **6** | **Xóa / Hủy lịch uống thuốc** | Trung bình | Thêm `DELETE /schedules/{id}` (chuyển trạng thái sang `archived`). | Bản gốc thiếu endpoint xóa khi bệnh nhân giảm số lần uống trong ngày. |
| **7** | **Sửa metadata đơn thuốc** | Trung bình | Thêm `PATCH /prescriptions/{id}` cho phép sửa `ngay_ke_don`, `noi_ke_don`. | Cho phép người dùng hoặc dược sĩ sửa lại thông tin sau khi OCR quét sai mà không ảnh hưởng danh mục thuốc con. |
| **8** | **Endpoint Upload ảnh OCR Blister** | Trung bình | Thêm `POST /patients/{patient_id}/prescriptions/ocr-upload` (Multipart file upload). | Phục vụ luồng quét vỉ thuốc on-device / backend OCR fallback với chuỗi nhận diện gợi ý (không ghi rác DB). |
| **9** | **Chuẩn hóa Soft-delete dữ liệu y tế** | Trung bình | Thay toàn bộ thao tác DELETE cứng tại `user-medications`, `conditions`, `schedules` thành Soft-delete (`trang_thai: 'active' \| 'archived'`). | Dữ liệu y tế và tuân thủ không được xóa vật lý để đảm bảo audit trail y khoa. |
| **10** | **Xử lý Bất đồng bộ Gợi ý Món ăn LLM** | Trung bình | `POST /patients/{patient_id}/meal-suggestions/generate` trả về `202 Accepted` kèm `job_id`; thêm `GET .../jobs/{job_id}` để poll. | LLM cần thời gian xử lý (3–10s), gọi đồng bộ sẽ vi phạm chỉ tiêu hiệu năng NFR04 (<= 2s). |
| **11** | **Hỗ trợ loại lịch thuốc khi cần (PRN)** | Nhỏ | Thêm `loai_lich: 'co_dinh' \| 'khi_can'` vào schema `MedicationSchedule`. | Chuẩn bị sẵn sàng cho thuốc hạ sốt, giảm đau dùng khi cần (đánh dấu TODO out-of-scope MVP). |
| **12** | **Quyền xuất bản sao dữ liệu cá nhân (Data Export)** | Nhỏ | Thêm `POST /users/me/data-export` và `GET .../jobs/{job_id}` (Async Job xuất file có link hạn 24h). | Tuân thủ quyền Data Portability theo Nghị định 356/2025/NĐ-CP, tránh timeout khi dữ liệu tuân thủ nhiều năm. |
| **13** | **Giới hạn phạm vi quyền ghi của Admin** | Nghiêm trọng | Tách permission `admin_override` riêng cho thao tác can thiệp dữ liệu lâm sàng của bệnh nhân. | Ngăn chặn việc tài khoản Admin sửa tùy tiện đơn thuốc, lịch uống bệnh nhân; mọi can thiệp đều có vết lý do rõ ràng. |
| **14** | **Audit trail cho luật tương tác (Bảng C/D/E)** | Nghiêm trọng | Bổ sung bảng `rule_change_logs`, đổi "Ghi Log" sang `rule_catalog`, thêm endpoint `GET /admin/rule-change-logs` phân trang. | Thay đổi ngưỡng liều hay cặp tương tác ảnh hưởng toàn bộ bệnh nhân; bắt buộc phải lưu vết ai đổi, giá trị cũ/mới để rollback. |
| **15** | **Vệ sinh vòng đời link-code & Chống dò phân tán** | Nghiêm trọng | Tự động hủy (`expired`) các mã cũ khi tạo mã mới; Thêm bộ đếm tự vô hiệu hóa mã (`LINK_CODE_INVALIDATED`) nếu bị nhập sai > 10 lần toàn cục. | Giảm diện tích tấn công dò mã (chỉ 1 mã active/bệnh nhân) và chặn triệt để tấn công phân tán (nhiều IP/tài khoản cùng dò 1 mã). |
| **16** | **Ràng buộc file cho OCR Upload** | Trung bình | Giới hạn dung lượng tối đa 10MB; Whitelist: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`; Vi phạm trả lỗi 422 chuẩn. | Ngăn chặn lạm dụng máy chủ, tải file độc hại hoặc file quá lớn gây sập tiến trình nhận diện hình ảnh. |
| **17** | **Chuyển `data-export` sang mô hình bất đồng bộ** | Trung bình | Thay thế `GET .../data-export` bằng mẫu Job `POST 202 Accepted` + Poll `GET .../jobs/{job_id}`, trả URL tải có hạn 24h. | Tránh lỗi HTTP Request Timeout khi bệnh nhân có hàng ngàn bản ghi `dose_logs` sau nhiều năm sử dụng. |
| **18** | **Chốt rõ RBAC phân tích phác đồ & xác nhận an toàn** | Trung bình | `POST regimens/analyze` đổi dứt khoát thành `read`; `PATCH recommendations/{id}/acknowledge` khóa chặt quyền `self` duy nhất. | Phân tích phác đồ là hàm thuần (không đổi dữ liệu); Xác nhận khuyến nghị an toàn là quyết định y tế cá nhân thuộc quyền tự quyết của bệnh nhân. |
| **19** | **Làm rõ luồng OCR và vòng đời Job Async** | Trung bình | `ocr-upload` chỉ trả preview (không lưu DB); `unmatched_scans` chỉ ghi khi lưu đơn; Job Async có enum chuẩn và timeout 60s. | Ngăn chặn rác database khi người dùng chụp thử nhiều lần và đảm bảo tiến trình nền không bị treo vô hạn. |
| **20** | **Chuẩn hóa Header dùng chung `X-Admin-Reason`** | Nghiêm trọng | Chuyển `ly_do` của Admin từ field trong body sang header HTTP `X-Admin-Reason: <string>` (min 10 ký tự), validate tập trung ở dependency. | Tránh lỗi HTTP DELETE bị proxy/gateway lược bỏ body; Pydantic không cần custom validator theo role người gọi; chuẩn hóa toàn diện API. |
| **21** | **Hạ quyền `ocr-upload` xuống `read`** | Trung bình | Đổi RBAC của `POST /prescriptions/ocr-upload` từ `write \| admin_override` thành `read (self/family/admin)`. Vẫn giữ ghi log `danh_sach_thuoc`. | Đây là hàm thuần nhận ảnh trả chuỗi preview (không lưu DB); cho phép người thân chỉ có quyền xem được quét thử đơn thuốc mới cho cha mẹ. |
| **22** | **Can thiệp Caregiver khẩn cấp & Four-Eyes Hậu Kiểm** | Nghiêm trọng | Mở rộng `PATCH /caregivers/{link_id}` cho `admin_override`: Chỉ được thu hẹp/thu hồi quyền; tự động gửi in-app notif cho bệnh nhân; bắt buộc Admin thứ 2 hậu kiểm trong 24h. | Bảo vệ người cao tuổi yếu thế bị lạm dụng quyền mà không thể tự thu hồi; giữ tốc độ xử lý khẩn cấp mà vẫn kiểm soát chéo quyền lực Admin. |
| **23** | **Chốt vòng đời mã Caregiver: Multi-use trong 15 phút** | Trung bình | Mã 6 số / QR là multi-use trong hạn 15 phút (cho phép nhiều người con cùng kết nối 1 mã); chỉ hết hạn khi quá 15p, sinh mã mới, hoặc bị dò sai > 10 lần. | Phù hợp bài toán thực tế gia đình có nhiều con cùng chăm sóc cha mẹ già, không bắt người già phải thao tác sinh mã lặp đi lặp lại. |
| **24** | **Chuẩn hóa Request Schema của HTTP DELETE** | Nhỏ | Xóa bỏ hoàn toàn phần Body trong schema của 3 endpoint DELETE (`conditions`, `user-medications`, `schedules`), chỉ giữ `Path: id`. | Tuân thủ triệt để nguyên tắc HTTP DELETE không body; lý do Admin can thiệp được truyền qua header `X-Admin-Reason`. |
| **25** | **Kiến trúc Giám sát Kép (Dual Supervision)** | Nghiêm trọng | Phân biệt mức giám sát: Caregiver Override dùng Four-Eyes ≤ 24h; Clinical Override dùng Tự động Re-Analysis (không cần Four-Eyes ở Phase 1). | Tránh phức tạp hóa bộ máy phê duyệt y tế lâm sàng trong khi vẫn đảm bảo an toàn tuyệt đối cho người cao tuổi. |
| **26** | **Hoàn thiện Four-Eyes Post-Review (3 trạng thái & 5 Guardrails)** | Nghiêm trọng | `POST /admin/audit-logs/{id}/post-review` hỗ trợ 3 trạng thái (`pending_post_review`, `reviewed_valid`, `reviewed_invalid`); 5 guardrails; chống tự hậu kiểm (`CANNOT_REVIEW_OWN_ACTION`). | Đảm bảo tính khách quan kiểm soát chéo giữa các Admin; khi invalid không tự động bật lại quyền mà tạo cờ compliance cảnh báo. |
| **27** | **Audit Trail cho chính thao tác Hậu Kiểm** | Trung bình | Mọi hành động post-review đều sinh một audit event độc lập trỏ tới `target_audit_log_id`, lưu vết quyết định và note của Admin hậu kiểm. | Minh bạch toàn diện quá trình giám sát; phục vụ cơ quan thanh tra y tế và bảo vệ dữ liệu cá nhân theo NĐ 356. |

---

## Chi Tiết Kỹ Thuật Từng Điểm (27 Mục)

### 1. Rate-Limiting trên Redeem Caregiver Code (Chống Brute-Force Theo Caller)
- **Cơ chế:** Lưu số lần nhập sai theo `(caller_user_id, client_ip)` trong cửa sổ trượt 15 phút (900 giây).
- **Ngưỡng:** Tối đa 5 lần thử sai. Đến lần thứ 6 trở đi trả về HTTP 429 `LINK_CODE_RATE_LIMITED`.

### 2. Phân Quyền Granular (Read vs Write) cho Caregiver
- Bảng `caregiver_links` bổ sung:
  - `cho_phep_chia_se: bool` (Mặc định `true` khi kết nối) — Quyền XEM.
  - `cho_phep_chinh_sua: bool` (Mặc định `false`, bệnh nhân phải chủ động bật) — Quyền GHI.
- Khi một Family Member gửi request ghi (thêm đơn thuốc, sửa liều, đổi giờ uống), `verify_patient_access` kiểm tra cờ `cho_phep_chinh_sua`. Nếu `false`, trả về `403 Forbidden` (`INSUFFICIENT_WRITE_PERMISSION`).

### 3. Per-item Batch Dose Sync Response
- Client gửi lên danh sách bản ghi offline (kèm `client_uuid`). Phản hồi trả về chi tiết trạng thái từng bản ghi `{client_uuid, status: 'synced'|'duplicate'|'error', error_code?, message?}`.

### 4. Tự Động Trigger Phân Tích Tương Tác
- Mọi thao tác thêm/sửa/xóa thuốc (`user_medications`) hoặc bệnh lý nền (`user_conditions`) đều tự động gọi hàm trigger phân tích an toàn (`_trigger_automatic_regimen_analysis`), tạo snapshot mới và cập nhật findings.

### 5. Phân Trang Chuẩn Hóa trên `access_logs` (NFR06, QA.09)
- Endpoint `GET /api/v1/admin/audit-logs` hỗ trợ đầy đủ các tham số query `page`, `page_size`, `patient_id`, `actor_role`, `from_date`, `to_date`.
- Dữ liệu trả về gói trong `PaginatedData[AuditLogResponse]`.

### 6. Soft-Delete Lịch Uống Thuốc (`schedules/{id}`)
- Thêm `DELETE /api/v1/schedules/{id}`. Cập nhật `trang_thai = 'archived'`, bảo tồn liên kết với các `dose_logs` đã uống trong quá khứ.

### 7. Chỉnh Sửa Metadata Đơn Thuốc (`prescriptions/{id}`)
- Thêm `PATCH /api/v1/prescriptions/{id}` sửa `ngay_ke_don`, `noi_ke_don` phục vụ sửa lỗi OCR mà không làm thay đổi danh sách thuốc con.

### 8. Luồng OCR Upload và Mối Quan Hệ với `unmatched_scans`
- `ocr-upload` nhận multipart file, thực thi OCR on-the-fly, trả về chuỗi văn bản + thuốc nhận diện gợi ý + các dòng chữ không nhận dạng được (`unmatched_lines`). Endpoint này **KHÔNG tự động lưu vào DB**.
- Chỉ khi người dùng bấm xác nhận tạo đơn thuốc (`POST /patients/{id}/prescriptions`) với thuốc tự nhập / thuốc không khớp, hoặc khi người dùng chủ động gửi (`POST /medications/unmatched-scans`), hệ thống mới ghi vào `unmatched_scan_logs` để Admin kiểm duyệt.

### 9. Chuẩn Hóa Soft-Delete Toàn Diện Cho Dữ Liệu Y Tế
- Toàn bộ các bảng dữ liệu lâm sàng của bệnh nhân (`user_conditions`, `user_medications`, `prescriptions`, `medication_schedules`) dùng `trang_thai: 'active' | 'archived'`. Mọi endpoint `DELETE` đều chuyển trạng thái thành `archived`, tuyệt đối không phát sinh lệnh SQL `DELETE FROM`.

### 10. Quản Lý Vòng Đời & Cơ Chế Timeout Job Bất Đồng Bộ (AI Meal Suggestion)
- Enum trạng thái chuẩn: `pending | processing | completed | failed`.
- Giới hạn thời gian xử lý tối đa là **60 giây**. Nếu quá 60s worker chưa hoàn tất, trạng thái job tự động đánh dấu `failed` với mã lỗi `JOB_TIMEOUT`.

### 11. Hỗ Trợ Thuốc Khi Cần (PRN - `loai_lich: co_dinh | khi_can`)
- Bổ sung trường `loai_lich: Literal['co_dinh', 'khi_can']`. Thuốc `khi_can` có `gio_uong` nullable, app không hẹn giờ báo thức định kỳ mà hiển thị nút "Ghi nhận uống thuốc khi cần" trên màn hình chính.

### 12. Quyền Xuất Bản Sao Dữ Liệu Cá Nhân (Data Portability - NĐ 356/2025)
- `POST /api/v1/users/me/data-export` khởi tạo job trích xuất dữ liệu nền (202 Accepted).
- `GET /api/v1/users/me/data-export/jobs/{job_id}` theo dõi tiến độ. Khi hoàn tất trả link tải file nén có chữ ký số tạm thời, **hết hạn sau 24 giờ**.

### 13. Giới Hạn Quyền Ghi của Admin (`admin_override`)
- Dữ liệu điều trị là bất khả xâm phạm. Admin quản trị hệ thống không có quyền tự ý sửa đơn thuốc, liều lượng, hay bệnh nền của bệnh nhân như một người dùng thông thường. Thao tác ghi của Admin được tách riêng thành quyền `admin_override`.

### 14. Nhật Ký Thay Đổi Luật Tương Tác Dược Lý (`rule_change_logs` & Rollback Audit)
- Mọi thao tác `POST`, `PUT`, `DELETE` trên các bảng luật an toàn (Bảng A, B, C, D) đều chuyển cột "Ghi Log?" thành **"Có (`rule_catalog`)"**.
- Bổ sung bảng `rule_change_logs` (`id`, `changed_by`, `table_name`, `record_id`, `action`, `old_value`, `new_value`, `thoi_gian`).
- Thêm endpoint `GET /api/v1/admin/rule-change-logs` (có phân trang) phục vụ hậu kiểm và rollback.

### 15. Quản Lý Vòng Đời Mã Caregiver & Chống Tấn Công Phân Tán (Dual Rate-Limit)
- **Vệ sinh vòng đời (Mã duy nhất):** Khi bệnh nhân sinh mã mới, hệ thống tự động chuyển toàn bộ mã active trước đó của bệnh nhân sang `expired`.
- **Rate-limit 2 lớp:**
  1. *Lớp 1 (Theo caller):* 5 lần sai / 15 phút → Khóa caller với `LINK_CODE_RATE_LIMITED` (HTTP 429).
  2. *Lớp 2 (Mã tự hủy):* Nếu một mã bị nhập sai quá **10 lần trên toàn hệ thống** (bất kể IP/caller), mã tự động chuyển sang `invalidated`. Mọi lần thử tiếp theo trả lỗi `LINK_CODE_INVALIDATED`.

### 16. Whitelist & Ràng Buộc Kích Thước File Cho Luồng OCR Upload
- Kích thước file tối đa: **10 MB**. Vượt quá trả về HTTP 422 `FILE_TOO_LARGE`.
- Whitelist định dạng MIME: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`. Không thuộc danh mục trả về HTTP 422 `UNSUPPORTED_FILE_TYPE`.

### 17. Chuyển Đổi Mô Hình Data Export Sang Asynchronous Job
- Thay thế hoàn toàn thiết kế đồng bộ cũ bằng quy trình xử lý nền 202 Accepted + poll job_id, trả `download_url` hết hạn sau 24h, tránh lỗi HTTP Request Timeout.

### 18. Giải Định Y Khoa: Quyền `read` Phân Tích Phác Đồ & Quyền `self` Khuyến Nghị An Toàn
- `POST /patients/{id}/regimens/analyze` là quyền `read` (hàm thuần, không đổi dữ liệu gốc, người thân có quyền xem được phép chạy).
- `PATCH /recommendations/{id}/acknowledge` chỉ dành riêng cho `self` (quyết định y tế cá nhân thuộc quyền tự quyết của bệnh nhân, tránh tranh chấp pháp lý khi xảy ra biến cố).

### 19. Xử Lý Tình Huống Ngoại Lệ & Timeout Cho Các Job Bất Đồng Bộ
- Thiết lập cơ chế timeout tự động (60s cho gợi ý bữa ăn, 300s cho trích xuất dữ liệu) chuyển sang `failed`, tránh treo tài nguyên hệ thống.

---

### 20. Chuẩn Hóa Header Dùng Chung `X-Admin-Reason` Cho Toàn Bộ Quyền `admin_override`
- **Vấn đề đã giải quyết:** Loại bỏ hoàn toàn field `ly_do` và `AdminOverrideReason` ra khỏi body của các Pydantic schema nghiệp vụ (Conditions, Prescriptions, User Medications, Schedules, Caregivers).
- **Cơ chế kỹ thuật:**
  - Client Admin truyền HTTP Header:
    ```http
    X-Admin-Reason: Sửa lại liều dùng theo biên bản hội chẩn bệnh viện ngày 21/09/2026
    ```
  - Dependency `verify_patient_access` thực hiện kiểm tra tập trung:
    ```python
    if actor_role == "admin" and required_permission in ("write", "admin_override"):
        if not x_admin_reason or len(x_admin_reason.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail={"code": "ADMIN_OVERRIDE_REASON_REQUIRED", "message": "Thao tác can thiệp của Admin bắt buộc phải có header X-Admin-Reason với độ dài tối thiểu 10 ký tự."}
            )
    ```
  - Header này hoạt động nhất quán trên **mọi HTTP Method** (`POST`, `PATCH`, `DELETE`) mà không lo bị các HTTP Proxy/Gateway lược bỏ body như đối với HTTP DELETE.
  - Giá trị của header được tự động ghi vào trường `ly_do_can_thiep` trong `access_logs`.

### 21. Hạ Quyền `ocr-upload` Xuống `read (self/family/admin)` Vì Bản Chất Hàm Thuần
- **Vấn đề đã giải quyết:** `POST /patients/{patient_id}/prescriptions/ocr-upload` chỉ nhận file ảnh/PDF vỉ thuốc và phân tích trả về preview cấu trúc (không lưu đơn thuốc hay chuỗi lỗi vào database).
- **Quyết định:** Hạ RBAC xuống **`read (self/family/admin)`** tương tự `POST regimens/analyze`.
- **Ý nghĩa nghiệp vụ:** Người thân đang chăm sóc cha mẹ (dù chỉ có quyền xem) vẫn có thể dùng camera điện thoại quét thử vỉ thuốc mới mua để xem hướng dẫn liều và kiểm tra tương tác thuốc trước khi đưa cho cha mẹ uống.
- **Audit Logging:** Vẫn giữ nguyên ghi log nhạy cảm vào `access_logs` với `data_scope: danh_sach_thuoc` vì đây là thao tác xử lý hình ảnh đơn thuốc thực tế của bệnh nhân.

### 22. Can Thiệp Caregiver Khẩn Cấp & Quy Trình Hậu Kiểm Four-Eyes 24h
- **Bảo vệ người dùng dễ tổn thương:** Đối tượng dùng Simple Mode là người cao tuổi có nguy cơ suy giảm nhận thức hoặc bị người chăm sóc lạm dụng quyền ghi thuốc. Bổ sung quyền `admin_override` trên `PATCH /caregivers/{link_id}`.
- **Ràng buộc an toàn nghiêm ngặt:**
  - Admin **CHỈ ĐƯỢC PHÉP THU HẸP HOẶC THU HỒI** quyền (`trang_thai: 'revoked'`, tắt `cho_phep_chia_se: false`, tắt `cho_phep_chinh_sua: false`).
  - Tuyệt đối **KHÔNG CHO PHÉP** Admin bật thêm quyền hoặc tạo mới liên kết thay bệnh nhân. Vi phạm trả về `403 CANNOT_EXPAND_PERMISSIONS_AS_ADMIN`.
- **Thông báo minh bạch (NĐ 356/2025/NĐ-CP):** Hệ thống tự động đẩy thông báo in-app cho bệnh nhân: *"Quản trị viên đã thực hiện thu hồi liên kết người thân [Tên Caregiver] vì lý do: [X-Admin-Reason]"*.
- **Quy trình Four-Eyes Hậu Kiểm trong 24h (Post-Action Maker-Checker):**
  - Giữ tốc độ xử lý khẩn cấp tức thì: Không yêu cầu duyệt trước (tránh chậm trễ cứu người).
  - Bản ghi can thiệp được lưu vào `access_logs` với `is_emergency_override: true` và `review_status: 'pending_post_review'`.
  - **Bắt buộc hậu kiểm:** Một Admin độc lập khác (khác với Admin thực hiện) phải thực hiện xác nhận hậu kiểm qua endpoint `POST /admin/audit-logs/{id}/post-review` trong vòng **24 giờ**.
  - Nếu sau 24h bản ghi vẫn ở trạng thái `pending_post_review`, hệ thống tự động kích hoạt cờ cảnh báo vi phạm kiểm soát nội bộ gửi đến kênh audit tuân thủ.

### 23. Vòng Đời Mã Caregiver: Multi-Use Trong Thời Hạn 15 Phút
- **Quyết định nghiệp vụ:** Mã liên kết 6 ký tự / QR do bệnh nhân tạo ra là **Multi-use** trong suốt thời hạn 15 phút.
- **Lý do thực tiễn:** Trong gia đình Việt Nam, người cao tuổi thường có từ 2–3 người con cùng tham gia chăm sóc. Khi cha mẹ sinh mã, cả con trai và con gái đều có thể quét cùng 1 mã trong 15 phút để kết nối vào hồ sơ, không bắt người già phải bấm sinh mã lặp đi lặp lại 3 lần.
- **Các điều kiện kết thúc vòng đời của mã:**
  1. Hết hạn thời gian (sau 15 phút kể từ lúc tạo).
  2. Bệnh nhân chủ động bấm sinh mã mới (mã cũ tự động chuyển `expired`).
  3. Mã bị nhập sai quá 10 lần trên toàn hệ thống (bị tấn công dò mã) → Mã tự động hủy (`invalidated`).

### 24. Chuẩn Hóa Request Schema của HTTP DELETE Không Body
- **Vấn đề đã giải quyết:** Loại bỏ toàn bộ `Body: Optional[AdminOverrideReason]` khỏi 3 endpoint DELETE:
  - `DELETE /patients/{patient_id}/conditions/{id}` → `Request Schema: Path: id`
  - `DELETE /user-medications/{id}` → `Request Schema: Path: id`
  - `DELETE /schedules/{id}` → `Request Schema: Path: id`
- **Lý do:** Toàn bộ lý do can thiệp y tế của Admin đã được chuyển sang header `X-Admin-Reason`. Schema của HTTP DELETE quay về chuẩn RESTful thuần túy, loại bỏ hoàn toàn nguy cơ lỗi do proxy lược bỏ HTTP body.

### 25. Phân Biệt Mức Giám Sát Giữa Caregiver Override và Clinical Admin Override (Kiến Trúc Dual Supervision)
- **Quyết định nghiệp vụ:** Không mở rộng cơ chế Four-Eyes 24h cho toàn bộ `admin_override` trong Phase 1.
- **Phân loại xử lý:**
  - **Caregiver Emergency Override (`PATCH /caregivers/{link_id}`):** Header `X-Admin-Reason` bắt buộc; Audit Log có; Tự động Re-analysis: Không áp dụng; **Four-Eyes hậu kiểm ≤ 24h: BẮT BUỘC**.
  - **Clinical Admin Override (`conditions`, `prescriptions`, `schedules`):** Header `X-Admin-Reason` bắt buộc; Audit Log có; **Tự động Re-analysis (Rule-based 0% LLM): BẮT BUỘC**; Four-Eyes: Không áp dụng ở Phase 1.
  - **Admin Catalog/Rule Change (`interactions`, `drug-foods`):** Theo chính sách Admin; Audit Log có (`rule_catalog`); Four-Eyes: Không áp dụng.
  - **Admin Audit Post-Review:** Header không áp dụng; Audit Log có; **Four-Eyes: Bắt buộc Admin độc lập khác**.
- **Lý do y tế & vận hành:** `PATCH /caregivers/{link_id}` có tính chất can thiệp khẩn cấp tức thời (bảo vệ người già bị lạm dụng quyền), không có cơ chế phân tích tự động nào kiểm tra lại quyết định, nên bắt buộc Admin thứ 2 hậu kiểm. Ngược lại, mọi can thiệp y tế lâm sàng đều tự động kích hoạt Rule Engine tạo snapshot tương tác và cập nhật findings ngay lập tức, nên không cần Four-Eyes làm nghẽn quy trình.

### 26. Hoàn Thiện Four-Eyes Post-Review (3 Trạng Thái & 5 Guardrails Chống Tự Hậu Kiểm)
- **Endpoint hậu kiểm:** `POST /api/v1/admin/audit-logs/{id}/post-review`
  - Body: `{"decision": "valid" | "invalid", "review_note": "..."}` (`review_note` tối thiểu 10 ký tự, tối đa 2000 ký tự).
- **3 trạng thái chuẩn (`review_status`):**
  1. `pending_post_review`: Đang chờ Admin thứ hai kiểm tra trong 24h.
  2. `reviewed_valid`: Admin thứ hai xác nhận hành động khẩn cấp là hợp lệ.
  3. `reviewed_invalid`: Admin thứ hai xác định hành động không hợp lệ / thiếu căn cứ.
- **Xử lý khi `reviewed_invalid`:**
  - Chuyển `review_status = 'reviewed_invalid'`.
  - Ghi nhận cờ vi phạm: `compliance_flags: ["COMPLIANCE_REVIEW_REQUIRED"]`.
  - Tạo thông báo nội bộ cho nhóm Quản trị / Pháp chế tuân thủ.
  - **Tuyệt đối KHÔNG tự động khôi phục liên kết caregiver** (mọi phục hồi quyền phải qua quy trình nghiệp vụ độc lập).
- **5 Guardrails kiểm soát bắt buộc:**
  1. `actor_role == admin`: Không phải Admin → `403 INSUFFICIENT_ADMIN_PERMISSION`.
  2. `reviewer_user_id != audit_log.actor_user_id`: Tự hậu kiểm chính mình → `403 CANNOT_REVIEW_OWN_ACTION`.
  3. `audit_log.is_emergency_override == true`: Không phải can thiệp khẩn cấp → `409 REVIEW_NOT_REQUIRED`.
  4. `audit_log.review_status == 'pending_post_review'`: Đã hậu kiểm rồi → `409 REVIEW_ALREADY_COMPLETED`.
  5. `now <= audit_log.review_deadline`: Quá hạn 24h tính từ timestamp server → `409 POST_REVIEW_DEADLINE_EXCEEDED` (Worker nền gắn cờ cảnh báo `POST_REVIEW_OVERDUE`, không tự đổi thành invalid).

### 27. Audit Trail Độc Lập Cho Chính Hoạt Động Hậu Kiểm
- **Nguyên tắc:** Quá trình kiểm soát cũng phải có audit log độc lập (Maker-Checker Audit Trail).
- **Cơ chế:** Khi Admin B thực hiện hậu kiểm bản ghi #1001 của Admin A, hệ thống tự động sinh thêm Event #1002 trong `access_logs`:
  - `actor_user_id = Admin B`
  - `actor_role = 'admin'`
  - `action = 'POST_REVIEW'`
  - `target_audit_log_id = 1001`
  - `review_decision = 'valid'` (hoặc `'invalid'`)
  - `review_note = "..."`
  - `data_scope = 'admin'`
- Đảm bảo cơ quan quản lý (Cục An toàn thông tin, Bộ Y tế theo NĐ 356) có thể truy vết toàn vẹn chuỗi giám sát nội bộ.

