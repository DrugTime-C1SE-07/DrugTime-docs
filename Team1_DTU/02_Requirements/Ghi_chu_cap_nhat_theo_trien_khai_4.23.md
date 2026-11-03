# Ghi chú cập nhật yêu cầu theo triển khai hiện tại — task 4.23

Ngày đối chiếu: **02/11/2026**. Phạm vi: onboarding mobile, nhắc thuốc, xác nhận và đồng bộ liều liên quan task 4.23.

Theo chỉ dẫn của người dùng, **lấy phần triển khai hiện tại làm trung tâm** khi cập nhật tài liệu sau này. File này ghi lại chỗ tài liệu đang khác hoặc chưa mô tả đủ hành vi đã có, kèm vị trí cần cập nhật và nguồn code. Đây là ghi chú cập nhật tài liệu, không phải bản sửa các QD/SRS gốc hay báo cáo đã kiểm thử thành công.

Các mô tả hiện trạng dưới đây được xác định bằng đọc code và contract; chưa được xác minh bằng chạy app trên LM G710 trong đợt đối chiếu này. Chỗ chưa thấy bằng chứng được ghi rõ, không suy ra chức năng đã có hoặc tự bổ sung nghiệp vụ.

## Mốc nguồn

| Repo | Commit dùng định vị nguồn |
|---|---|
| `frontend` | `b1605b6970c86f0a86cc9203fb2bea41cd20bb03` |
| `backend` | `fa64ce2bf858063e66ee9a4d5fabf08bc0ac69d1` |
| `api_contract` | `41ce5d00041cb65b2872505871ed99018882bcc0` |
| `docs` trước khi thêm ghi chú | `965ace005d98f0b01d0226f3c07a5b0a9f14de62` |

Chi tiết được lấy từ nội dung checkout đã đọc ngày đối chiếu; commit giúp định vị repo, không thay thế bằng chứng chạy thực tế. Đường dẫn `frontend/...`, `backend/...`, `api_contract/...` tính từ gốc superproject DrugTime.

Tài liệu cần cập nhật chính:

- [Quyết định nghiệp vụ theo chức năng](drugtime_quyet_dinh_theo_chuc_nang.md).
- [SRS](<Software Requirements Specification/DrugTime_SRS.docx>): UC.01, UC.02, UC.10, UC.11 và các mô tả dữ liệu liên quan.
- [Test Plan](../04_Quality_&_Testing/DrugTime_Test_Plan.docx) và Test Cases: xem [ghi chú cập nhật kiểm thử](../04_Quality_&_Testing/Ghi_chu_cap_nhat_kiem_thu_4.23.md).

## DT423-01 — Mobile đăng nhập bằng OTP

- **Tài liệu đang ghi:** QD-44, mục 1 quy định email + mật khẩu và hoãn đăng nhập số điện thoại. Test Plan, Scope of test → Authenticate User ghi email/password. SRS UC.01 còn mô tả chọn loại tài khoản và hỗ trợ OAuth; không dùng mô tả này để suy ra mobile đã có các bước tương ứng.
- **Triển khai hiện tại:** mobile yêu cầu OTP bằng `phone` hoặc `email` qua `POST /auth/mobile/otp`, xác minh bằng `POST /auth/mobile/verify`. Khi `profile_complete` chưa đạt thì vào màn hoàn thiện hồ sơ; hồ sơ gửi qua `POST /auth/profile`. Điều hướng dùng `needsProfile`; consent được xử lý bằng cổng consent hiện có.
- **Cần cập nhật sau:** viết lại luồng đăng nhập/onboarding mobile theo OTP, phân biệt tài khoản chưa/đã hoàn tất hồ sơ và xử lý consent. Đối chiếu bước chọn vai trò/OAuth với UI thực tế trước khi giữ chúng trong UC.01. Không áp dụng thay đổi OTP này cho Admin Web: contract có API đăng nhập admin riêng.
- **Nguồn triển khai:** `frontend/mobile/lib/features/auth/data/sources/auth_api_service.dart` (`requestMobileOtp`, `verifyMobileOtp`, `completeProfile`); `frontend/mobile/lib/features/auth/presentation/screens/otp_verification_screen.dart` (`_showSuccessAndNavigate`); `complete_profile_screen.dart`; `frontend/mobile/lib/features/consent/presentation/widgets/consent_gate.dart`; `api_contract/openapi.json`.
- **Đã chốt trong hội thoại:** người dùng chọn luồng OTP hiện có làm kỳ vọng của task 4.23. Không suy ra quy tắc khôi phục mật khẩu/OAuth của QD-44 cũng đã được thay thế hoặc triển khai.

## DT423-02 — Nút nhắc lại do người dùng thao tác

- **Tài liệu đang ghi:** QD-20, mục 6.1: tự nhắc lại một lần sau 10 phút. Mục 5 còn ghi chủ động hoãn liều được hoãn sang giai đoạn sau.
- **Triển khai hiện tại:** màn nhắc có nút **“Nhắc lại sau 10 phút”**. `DoseReminderController.snooze()` lấy thời điểm thao tác cộng 10 phút rồi gọi scheduler cho các mục trong nhóm. Scheduler giữ `scheduled_at` gốc và thay thời điểm nhắc. Hàm này không có bộ đếm giới hạn một lần; nó không tự chứng minh có tác vụ tự nhắc khi người dùng chưa bấm nút.
- **Cần cập nhật sau:** tách rõ “người dùng bấm nhắc lại” và “tự động nhắc lại”; mô tả nhánh đã có là thao tác người dùng, không đổi giờ dự kiến uống và không ghi xác nhận đã uống. Không ghi cơ chế tự động hoặc giới hạn một lần là đã triển khai nếu chưa tìm được bằng chứng riêng.
- **Nguồn triển khai:** `frontend/mobile/lib/features/reminder/presentation/screens/dose_reminder_screen.dart` (`_snooze`, `_buildActions`); `presentation/state/dose_reminder_controller.dart` (`snooze`); `frontend/mobile/lib/core/notification/reminder_notification_scheduler.dart` (`snooze`).
- **Đã chốt trong hội thoại:** dùng luồng hiện có thay kỳ vọng QD-20 cũ cho task 4.23.

## DT423-03 — Xác nhận từng thuốc, một phần nhóm hoặc tất cả

- **Tài liệu đang ghi:** QD-21, mục 6.1 chỉ xác nhận từng thuốc, chưa có nút “xác nhận tất cả”. SRS UC.11 mô tả xác nhận một liều, chưa mô tả chi tiết lựa chọn nhiều thuốc.
- **Triển khai hiện tại:** màn nhắc khởi tạo lựa chọn cho các thuốc trong nhóm; có xác nhận từng mục, các mục đang chọn và nút **“Đã uống cả … thuốc”**. `confirmAll()` lưu tuần tự từng mục chưa xác nhận; phần đã lưu thành công được giữ khi phần khác lỗi. Đây không phải thao tác nguyên tử “mọi thuốc cùng thành công hoặc cùng rollback” ở tầng UI.
- **Cần cập nhật sau:** sửa QD-21 và bổ sung UC.11 về nhóm/lựa chọn; ghi rõ kết quả từng thuốc và hành vi lỗi một phần. Phân biệt xác nhận cục bộ với kết quả đồng bộ máy chủ.
- **Nguồn triển khai:** `frontend/mobile/lib/features/reminder/presentation/screens/dose_reminder_screen.dart` (`initState`, `_buildActions`); `presentation/state/dose_reminder_controller.dart` (`confirmItem`, `confirmAll`, `_confirm`); `frontend/mobile/lib/core/storage/local_db/sqlite_dose_outbox.dart`.
- **Đã chốt trong hội thoại:** dùng hành vi chọn một phần/xác nhận tất cả hiện có làm kỳ vọng của task 4.23.

## DT423-04 — Phân biệt thông báo hệ điều hành và nhóm thuốc trong màn nhắc

- **Tài liệu đang ghi:** QD-21 nói gom thuốc cùng giờ thành **một thông báo**.
- **Triển khai hiện tại:** `scheduleOccurrences()` đặt thông báo cho từng occurrence, với ID từ lịch và thời điểm dự kiến. Khi mở một payload, `_handleNotificationPayload()` tìm các lịch cùng bệnh nhân/cùng mốc giờ để dựng nhóm thuốc trên màn nhắc, loại các cữ đã có bản ghi cục bộ. Có màn nhắc nhóm không đồng nghĩa đã gom thành một thông báo ở hệ điều hành.
- **Cần cập nhật sau:** mô tả riêng hai bước lập thông báo và dựng nhóm UI. Khi mô tả số lượng thông báo thực xuất hiện trên máy, bổ sung kết quả đo trên thiết bị; không lấy nhóm UI làm bằng chứng đã đạt câu “một thông báo”.
- **Nguồn triển khai:** `frontend/mobile/lib/core/notification/reminder_notification_scheduler.dart` (`scheduleOccurrences`); `frontend/mobile/lib/core/notification/notification_id.dart`; `frontend/mobile/lib/app/app.dart` (`_handleNotificationPayload`).

## DT423-05 — “Bỏ qua liều này” hiện là đóng màn nhắc

- **Tài liệu đang ghi:** mục 5 còn để mở nghiệp vụ bỏ qua liều. SRS UC.11, Alternative Flow 2 cho phép rời luồng mà không ghi xác nhận.
- **Triển khai hiện tại:** nút **“Bỏ qua liều này”** gọi `skip()`, trả `DoseReminderResult.skipped` và đóng màn. Nhánh này không gọi outbox để ghi đã uống, không tự tạo `bo_lo`. `skipped` là kết quả điều hướng UI, không phải trạng thái liều trên API/DB.
- **Cần cập nhật sau:** giải thích rõ ý nghĩa nút và liên hệ với nhánh rời luồng của UC.11; không bổ sung trạng thái liều “bỏ qua” chỉ từ nhãn nút. Việc Worker xác định bỏ lỡ là luồng khác.
- **Nguồn triển khai:** `frontend/mobile/lib/features/reminder/presentation/state/dose_reminder_controller.dart` (`skip`); `presentation/screens/dose_reminder_screen.dart` (`_skip`); `frontend/mobile/lib/features/reminder/domain/entities/dose_reminder.dart` (`DoseReminderResult`).

## DT423-06 — Bản ghi quá 120 phút chưa thể hiện đầy đủ hồ sơ riêng của QD-10

- **Tài liệu đang ghi:** QD-10 và tiêu chí biên mục 5 yêu cầu giữ `bo_lo` đồng thời ghi nhận riêng thời điểm thao tác, thời điểm uống khai báo và nguồn ghi nhận.
- **Triển khai hiện tại:** với liều được tính `MISSED`, adapter ghi `taken_at = NULL` vào `dose_logs`; contract cũng mô tả quá +120 phút ghi `bo_lo`, không lưu `taken_at`, `adherence_counted=false`. Khi đã có liều `da_uong`/`uong_tre`, upsert giữ kết quả đã xác nhận. Trong đường ghi đã đọc, chưa thấy hồ sơ riêng bảo toàn đầy đủ các trường mà QD-10 yêu cầu.
- **Cần cập nhật sau:** ghi đúng dữ liệu máy chủ đang lưu, cửa sổ tính trạng thái và nhánh giữ nguyên kết quả cũ. Tách phần “hiện trạng đã có” khỏi yêu cầu hồ sơ riêng chưa được chứng minh. Không dùng việc contract khớp code để khẳng định đã đáp ứng toàn bộ QD-10; chưa có bằng chứng thì không điền tên bảng/luồng hồ sơ riêng.
- **Nguồn triển khai:** `backend/src/drugtime/modules/adherence/domain/dose.py` (`status_for_confirmation`, `status_after_confirmation`); `adapters/outbound/sql_adherence.py` (`SqlDoseLogs.upsert_confirmation`, `_UPSERT_CONFIRMATION`); `api_contract/openapi.json`, `POST /doses/batch`.

## DT423-07 — Tên endpoint và kết quả đồng bộ liều

- **Tài liệu đang ghi:** mục 14, Ch.10/MT-03 còn nêu `/api/v1/dose-logs/batch-sync` ở trạng thái đề xuất.
- **Triển khai hiện tại:** mobile và Backend dùng `POST /doses/batch`. Body là mảng có `client_uuid`, **`schedule_id`**, `scheduled_at`, `taken_at`. Kết quả có `items` và `summary`; HTTP 200 có thể kèm mục lỗi, mã lỗi từng mục nằm trong `error.http_status`. Có thêm `POST /doses/sync-checkpoints`, không nhận giờ client và trả 204 khi thành công. Hai API đã có trong contract hiện tại; không còn tình trạng “thiếu hai endpoint trong contract”.
- **Cần cập nhật sau:** sửa tham chiếu endpoint cũ trong sổ quyết định/SRS/tài liệu kiểm thử; phân biệt `schedule_id` trên API với `medication_schedule_id` trong lưu trữ. Mô tả checkpoint theo contract, không coi HTTP 200 là toàn mẻ đã đồng bộ. Trạng thái duyệt của MT-03 cần chủ tài liệu cập nhật, không tự đổi bằng ghi chú này.
- **Nguồn triển khai:** `frontend/mobile/lib/core/sync/sync_engine.dart` (`DoseApiRemoteDataSource`, `_toBackendPayload`); `backend/src/drugtime/modules/adherence/adapters/inbound/http.py` (`post_doses`, `post_sync_checkpoint`); `api_contract/openapi.json`.
- **Đã chốt trong hội thoại:** dùng contract hiện tại tại commit nêu ở đầu file làm chuẩn kiểm thử 4.23.

## DT423-08 — Ghi access log có phân biệt chính chủ và từng loại truy cập

- **Tài liệu đang ghi:** QD-33, mục 9 mô tả audit cho truy cập của bệnh nhân nói chung; bất biến 2 trong `AGENTS.md` của superproject yêu cầu Access Log Writer trên đường dữ liệu sức khỏe.
- **Triển khai hiện tại:** hai API ghi liều/checkpoint vẫn đi qua kiểm quyền và consent. Tuy nhiên chúng khai báo `x-health-audit-self=false`; adapter ghi dùng `audit_self` mặc định false. Luồng `authorize()` chỉ gọi writer khi `decision.log_role` có giá trị. Đọc lịch sử qua `authorize_history()` lại truyền `audit_self=True`. Vì vậy không thể viết “mọi lần chính chủ ghi liều thành công đều có dòng access log” dựa trên triển khai này.
- **Cần cập nhật sau:** lập ma trận endpoint × chủ thể × quyền × điều kiện ghi log theo code, phân biệt đi qua PEP với có ghi audit. Ghi rõ chỗ còn khác QD-33/bất biến khi cập nhật tài liệu; ghi chú này không tự xác nhận ngoại lệ đã được phê duyệt hay tự bỏ yêu cầu audit/fail-closed.
- **Nguồn triển khai:** `backend/src/drugtime/modules/adherence/adapters/inbound/http.py`; `adapters/outbound/other_modules.py` (`authorize_history`, `authorize_dose_write`, `authorize_sync_checkpoint`); `backend/src/drugtime/modules/access/api.py`; `application/authorize.py`; `domain/rules.py` (`decide`).

## DT423-09 — Giới hạn so sánh `taken_at` khi phát lại UUID của bản ghi `bo_lo`

- **Tài liệu đang ghi:** QD-14 và contract mô tả cùng UUID nhưng khác nội dung là xung đột 409.
- **Triển khai hiện tại:** khi tìm được bản ghi theo UUID, `SqlDoseLogs.upsert_confirmation()` so `schedule_id`, `scheduled_at`; phép so `taken_at` chỉ thực hiện nếu trạng thái đã lưu **khác `MISSED`**. Với bản ghi `bo_lo`, giá trị `taken_at` không được lưu và không tham gia phép so này. Validation thời gian ở application vẫn chạy trước khi tới adapter.
- **Cần cập nhật sau:** ghi riêng nhánh này khi mô tả mức bảo đảm idempotency hiện tại; không khẳng định mọi thay đổi `taken_at` đều bị 409. Đánh dấu sự khác nhau giữa mô tả contract và code để chủ tài liệu xử lý, không tự suy ra đây là ngoại lệ nghiệp vụ đã được chốt hoặc sửa code trong lượt ghi chú.
- **Nguồn triển khai:** `backend/src/drugtime/modules/adherence/application/confirm_doses.py` (`confirm_doses`); `adapters/outbound/sql_adherence.py` (`SqlDoseLogs.upsert_confirmation`); `api_contract/openapi.json`, mô tả idempotency của `POST /doses/batch`.

## Khi cập nhật tài liệu gốc

Với từng mã DT423, cập nhật câu chữ/use case/bảng/test case ở vị trí đã chỉ ra, rồi ghi tham chiếu tới nguồn triển khai mới nhất. Phần code và contract đang khác nhau phải được giữ rõ cả hai phía đến khi có quyết định xử lý; không ghi thành một hành vi thống nhất nếu thực tế chưa thống nhất. Những cam kết chưa đo trên thiết bị hoặc chưa có hồ sơ lưu trữ chứng minh phải giữ đúng trạng thái đó.
