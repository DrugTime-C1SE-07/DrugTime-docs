# Ghi chú cập nhật tài liệu kiểm thử theo triển khai — task 4.23

Ngày đối chiếu: **02/11/2026**. Nguồn hành vi là code hiện tại và `api_contract/openapi.json` tại commit `41ce5d00041cb65b2872505871ed99018882bcc0`. Chi tiết sai khác, vị trí tài liệu và nguồn code nằm trong [ghi chú yêu cầu](../02_Requirements/Ghi_chu_cap_nhat_theo_trien_khai_4.23.md).

File này để cập nhật [DrugTime Test Plan](DrugTime_Test_Plan.docx), [Test Plan còn lại trong cùng thư mục](Test_Plan.docx) và [Test Cases tổng](Test_Cases.xlsx) sau này. Nội dung `DrugTime_Test_Plan.docx` đã được đọc để đối chiếu; `Test_Plan.docx` và từng dòng trong workbook chưa được rà soát toàn bộ trong lượt này, nên các mục dưới đây là nơi cần đối chiếu/bổ sung, không khẳng định từng file đều đang có cùng một lỗi.

Chưa chạy các ca trên LM G710 trong lượt lập ghi chú; các dòng dưới đây không mang trạng thái Pass/Fail thực tế.

## Môi trường cần bổ sung vào hồ sơ đợt chạy

Người dùng đã chốt **LM G710, Android 13, Backend local trên máy tính qua USB** cho 4.23. Ghi model/build thực tế, app version/commit/build type, Backend/contract version, API base URL thực, quyền thông báo/hẹn giờ, pin/mạng và mốc giờ khi chạy. App cần dùng luồng sản phẩm với `DRUGTIME_PREVIEW=false`; không dùng dữ liệu preview hoặc entrypoint Timer thử riêng để kết luận đã đạt end-to-end.

Đây là một cấu hình của PB30. Giữ riêng ca iOS thuộc 4.24 và các thiết bị Android khác; không sửa mục tiêu Android + iOS chung thành “đã bao phủ đủ” chỉ vì đã chạy một LM G710.

## Các nhóm test cần cập nhật theo hành vi hiện tại

| Mã đối chiếu | Vị trí tài liệu cần cập nhật | Nội dung cần phản ánh trong test |
|---|---|---|
| DT423-01 | Test Plan → Scope of test → Authenticate User; Mobile Application → Welcome & Onboarding; nhóm test đăng nhập/đăng ký | Mobile dùng OTP qua SĐT/email, không dùng kỳ vọng email/password. Tách gửi OTP, xác minh, dữ liệu sai/hết hạn, hồ sơ chưa hoàn tất, consent và mở lại phiên. Dịch vụ OTP chưa sẵn sàng thì ghi Blocked. Không dùng tài khoản admin để chứng minh luồng mobile. |
| DT423-02 | Nhóm reminder/hoãn nhắc; test dẫn QD-20 | Tách bấm nút “Nhắc lại sau 10 phút” khỏi tự nhắc khi không có thao tác. Kiểm thời điểm nhắc mới tính từ lúc bấm; `scheduled_at` gốc được giữ, không ghi đã uống. Không đánh Pass cơ chế tự nhắc một lần chỉ từ việc bấm nút thành công. |
| DT423-03 | Nhóm xác nhận liều; test dẫn QD-21; UC.11 | Có ca một thuốc, một phần nhóm, tất cả; lỗi lưu một phần giữ kết quả đã lưu và thử lại phần lỗi. Phân biệt thành công lưu cục bộ với ACK máy chủ. Không đặt kỳ vọng cả nhóm rollback nguyên tử. |
| DT423-04 | Nhóm nhiều thuốc cùng giờ | Đếm thông báo thực tế trên OS riêng với số thuốc trong màn nhắc. Kiểm mở một thông báo dựng đúng nhóm và loại các cữ đã có bản ghi. Nhóm UI không chứng minh chỉ có một thông báo trên OS. |
| DT423-05 | Nhóm “bỏ qua”/rời màn xác nhận | Bấm “Bỏ qua liều này” đóng màn; không sinh bản ghi đã uống hoặc `bo_lo` chỉ do nút này. Không thêm trạng thái liều `skipped` từ kết quả điều hướng UI. |
| DT423-06 | Nhóm biên −30/+30/+120 phút; bằng chứng ghi nhận muộn | Kiểm API/DB: trước −30 bị từ chối; −30…+30 là `da_uong`; trên +30 đến +120 là `uong_tre`; quá +120 theo contract là `bo_lo`, `adherence_counted=false`, không lưu `taken_at` ở bản ghi đó. Tách ca liều đã xác nhận trước vì upsert giữ kết quả cũ. Không đánh Pass phần hồ sơ riêng QD-10 khi chưa có bằng chứng. |
| DT423-07 | Nhóm đồng bộ liều/contract | Gọi `/doses/batch` với trường `schedule_id`, đọc `items`, `summary`, lỗi từng mục. HTTP 200 không chứng minh mọi mục đã lưu. Ghi riêng `/doses/sync-checkpoints`: không body/giờ client, 204, thời điểm máy chủ không lùi, chỉ gửi khi hàng chờ đáp ứng điều kiện contract. Thay tham chiếu `/api/v1/dose-logs/batch-sync` nếu còn. |
| DT423-08 | Nhóm PEP/consent/audit | Tách truy cập đọc lịch sử (`audit_self=True`) khỏi chính chủ ghi liều/checkpoint (`audit_self=False`). Xác định nhánh nào có gọi writer trước khi mô phỏng lỗi writer. Phản ánh sai khác với QD-33/bất biến dự án bằng một phát hiện rõ ràng; không khẳng định toàn bộ audit đã đạt từ response thành công. |
| DT423-09 | Nhóm phát lại UUID/thay payload | Có ca UUID trỏ tới `bo_lo` và đổi `taken_at` hợp lệ: ghi kết quả adapter thực trả, không mặc định 409 như mọi nhánh. Tách các trường `schedule_id`/`scheduled_at` vẫn được so. Sai khác code–contract phải xuất hiện trong báo cáo, không giấu bằng cách chỉ chạy ca UUID trỏ tới liều đã uống. |

## Thông báo trên Android 13 và số liệu thời gian

`DrugTime_Test_Plan.docx`, Quality Objectives hiện nêu lệch giờ nhắc ≤2 giây và phản hồi UI p95 ≤2 giây. Giữ chúng là tiêu chí của tài liệu; đọc code chưa chứng minh đã đạt hai mốc này trên LM G710.

Scheduler thử `exactAllowWhileIdle`; khi lời gọi lập nhắc phát sinh ngoại lệ, nhánh `catch` dùng `inexactAllowWhileIdle`. Khi cập nhật test, ghi quyền và chế độ thực dùng. Không coi việc gọi nhánh dự phòng thành công là bằng chứng đạt mốc lệch ≤2 giây; không tự hạ mốc trong Test Plan chỉ để khớp kết quả chưa đo.

Tách các điều kiện foreground, background, màn hình khóa/tắt, vuốt khỏi recent apps và offline. Phân biệt chúng với Force stop trong Settings. Việc khai báo receiver khởi động lại/full-screen intent trong manifest chưa chứng minh delivery, quyền hoặc khả năng hoạt động trong mọi chế độ pin.

Nội dung mặc định của scheduler là chung chung; cổng màn hình khóa phải được kiểm riêng trên máy thật trước khi kết luận không lộ tên thuốc/liều. Widget test/mock không thay thế kết luận này.

## Cách cập nhật kết quả để sử dụng về sau

- Mỗi test case ghi mã DT423 liên quan, nguồn code/contract và phiên bản đã chạy; mong đợi nào theo triển khai, điểm nào còn khác tài liệu cũ cần được thấy rõ.
- Ghi thực tế và bằng chứng riêng; dùng đúng Pass/Fail/Blocked/Not Run/N/A. Các ghi chú hiện trạng trong file này không phải dữ liệu “Actual Result”.
- Lỗi tìm được liên kết tới hồ sơ lỗi/task 4.25. Điểm khác tài liệu được người dùng chọn lấy triển khai làm chuẩn vẫn cần cập nhật tài liệu nguồn; điểm code–contract chưa thống nhất vẫn phải giữ cả hai phía trong báo cáo.
- Khi cập nhật xong một mục trong tài liệu gốc, dẫn phiên bản và đánh dấu mục ghi chú tương ứng đã xử lý. Không tự đánh dấu hoàn thành chỉ vì file ghi chú đã được tạo.
