# DrugTime — Quyết định nghiệp vụ nhóm theo chức năng

*   **Nguồn:** `drugtime_ho_so_quyet_dinh_chi_tiet.md` — bản 3.1, baseline `QD-2026-10-03-v1` (03/10/2026)
*   **Phạm vi:** 46 quyết định QD (Chương 12), các quyết định "Đồng ý" ở Chương 1, quyết định thống nhất hợp đồng API (Chương 10), các đề xuất còn chờ Mentor duyệt và các phần còn mở.

**Quy ước trạng thái**

| Ký hiệu | Ý nghĩa |
|---|---|
| ✅ | Đã chốt trong baseline `QD-2026-10-03-v1`; chưa xác nhận đã triển khai, chưa có chữ ký Mentor |
| 🆕 | Nhóm chốt bổ sung ngày 04/10/2026 để xử lý điểm không nhất quán; chưa nằm trong baseline `QD-2026-10-03-v1`, cần ghi vào sổ gốc |
| ☑️ | Ghi "Đồng ý" ở cột Mentor từ lần rà soát trước (không thuộc đợt chốt 03/10) |
| ⏳ | Mới là đề xuất, ô Mentor còn trống `[ ] Đồng ý / [ ] Điều chỉnh` |
| ❓ | Phần còn cần đặc tả/làm rõ |

**Mục lục chức năng**

1. [Tài khoản & xác thực](#1-tài-khoản--xác-thực)
2. [Danh mục thuốc](#2-danh-mục-thuốc)
3. [Nhập thuốc: OCR & nhập tay](#3-nhập-thuốc-ocr--nhập-tay)
4. [Lịch uống thuốc](#4-lịch-uống-thuốc)
5. [Xác nhận liều & trạng thái liều](#5-xác-nhận-liều--trạng-thái-liều)
6. [Nhắc thuốc & thông báo](#6-nhắc-thuốc--thông-báo)
7. [Ngoại tuyến & đồng bộ](#7-ngoại-tuyến--đồng-bộ)
8. [Người thân: liên kết & chia sẻ](#8-người-thân-liên-kết--chia-sẻ)
9. [Đồng ý, kiểm toán & phân quyền](#9-đồng-ý-kiểm-toán--phân-quyền)
10. [Xóa tài khoản & lưu giữ dữ liệu](#10-xóa-tài-khoản--lưu-giữ-dữ-liệu)
11. [Tương tác thuốc & gợi ý món ăn](#11-tương-tác-thuốc--gợi-ý-món-ăn)
12. [Báo cáo tuân thủ](#12-báo-cáo-tuân-thủ)
13. [Chế độ đơn giản](#13-chế-độ-đơn-giản)
14. [Hợp đồng API & dữ liệu](#14-hợp-đồng-api--dữ-liệu)
15. [Hạ tầng & kiến trúc nền](#15-hạ-tầng--kiến-trúc-nền)
16. [Quản trị phạm vi, tài liệu & nghiệm thu](#16-quản-trị-phạm-vi-tài-liệu--nghiệm-thu)
17. [Điểm không nhất quán phát hiện khi gom nhóm](#17-điểm-không-nhất-quán-phát-hiện-khi-gom-nhóm)
18. [Bảng tra QD → chức năng](#18-bảng-tra-qd--chức-năng)

---

## 1. Tài khoản & xác thực

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-44 | Một tài khoản có thể vừa quản lý thuốc của mình vừa là người thân của người khác; quyền tính theo từng quan hệ. Tài khoản admin tách riêng khỏi tài khoản cá nhân. | ✅ | CS-06, BQ-051, XSD-14, MT-17 |
| QD-44 | Giai đoạn 1 dùng email + mật khẩu, có xác minh email; khôi phục bằng liên kết dùng một lần, hết hạn sau 15 phút; thu hồi mọi phiên sau đổi mật khẩu. | ✅ | BQ-052 |
| QD-44 | Hoãn đăng nhập bằng số điện thoại/OAuth; không dùng mã liên kết người thân làm thông tin khôi phục. Khi còn dữ liệu chờ đồng bộ, khôi phục phải đưa về đúng tài khoản (theo QD-06). | ✅ | BQ-052 |

**Còn mở:** ❓ Hợp đồng xử lý email trùng và chuẩn hóa định danh (BQ-052).

---

## 2. Danh mục thuốc

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-36 | Giữ ID nội bộ và snapshot thuốc gắn với lịch sử. Thuốc mất/đổi ở nguồn → đánh dấu ngừng chọn mới hoặc tạo phiên bản; không xóa dây chuyền, không tự dừng lịch điều trị đang có. | ✅ | BQ-038, BQ-039, HBR-16, MT-08, XSD-08 |
| QD-36 | Đồng bộ danh mục: cách ly từng dòng lỗi, tiếp tục các dòng độc lập hợp lệ, có báo cáo đối soát. | ✅ | BQ-038 |
| QD-38 | Chỉ dùng đơn vị chuẩn, giá trị dương; tách hàm lượng khỏi số lượng dùng. Không tự quy đổi đơn vị khác chiều, không đổi viên/ml sang mg nếu thiếu hàm lượng/nồng độ đã xác minh. Mọi quy đổi được hỗ trợ phải có quy tắc rõ và hiển thị cho người dùng xác nhận. | ✅ | BQ-042 |
| C-01 | Đồng bộ danh mục theo bản RabbitMQ, chuyển task 1.18 sang Sprint 2 (mã 2.21). | ☑️ | PB06 |

**Còn mở:** ❓ Danh sách cụ thể đường dùng, dạng bào chế và các phép quy đổi được hỗ trợ (BQ-042).

---

## 3. Nhập thuốc: OCR & nhập tay

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-39 | Mọi kết quả OCR **và** nhập tay phải được người dùng kiểm tra tên thuốc, hàm lượng, đơn vị, liều và giờ trước khi tạo lịch. | ✅ | C-17, BQ-043, HBR-07, HBR-08 |
| QD-39 | Giai đoạn 1 chỉ tạo lịch cho thuốc đã có trong danh mục. Thuốc chưa có → giữ ở bản nháp và gửi yêu cầu bổ sung danh mục; không gán thuốc gần giống để vượt chặn. | ✅ | BQ-044, HBR-15, MT-07 |
| QD-39 | Ảnh và văn bản OCR chỉ lưu mã hóa tối đa 24 giờ, xóa ngay khi xác nhận hoặc hủy; bản nháp chỉ giữ các trường người dùng đã kiểm tra. | ✅ | XSD-12, LDR-07 |
| QD-39 | Không khôi phục màn hình Admin duyệt thuốc quét không khớp. | ✅ | C-17, MT-07, biên bản mục 7 |

---

## 4. Lịch uống thuốc

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-15 | Một dòng lịch = một giờ uống của một thuốc. Ba lần/ngày là ba dòng, cùng nhóm phác đồ, có ngày hiệu lực và phiên bản. | ✅ | BQ-012, HBR-04, HBR-22, BQ-007 |
| BS-02 | Chỉ dùng một múi giờ `Asia/Ho_Chi_Minh` cho toàn hệ thống; không lưu múi giờ theo từng dòng lịch. Phần "múi giờ" trong QD-15 được hiểu theo C-10. | 🆕 | QD-15, C-10, HBR-23 |
| QD-16 | Khoảng hiệu lực nửa mở `[bắt đầu, kết thúc)`; sửa lịch tạo phiên bản mới. | ✅ | BQ-013, BQ-014 |
| QD-16 | Khi sửa: giữ liều quá khứ; hủy liều tương lai chưa có ghi nhận kể từ thời điểm thay đổi có hiệu lực; không xóa liều đã xác nhận sớm. Liều đã đến giờ vẫn xác nhận theo cửa sổ cũ (quá 120 phút theo QD-10, bản ngoại tuyến theo QD-11–13). | ✅ | BQ-015, BQ-057, SY-09 |
| QD-16 | Giao dịch sửa lịch và đối soát phải kiểm tra phiên bản để tránh sinh/hủy trùng liều. | ✅ | HBR-05, XSD-02 |
| C-10 | Cố định múi giờ `Asia/Ho_Chi_Minh` cho lịch, thứ và hiển thị nghiệp vụ; đổi múi giờ thiết bị không đổi lịch điều trị; không cấu hình múi giờ theo bệnh nhân. | ☑️ | BQ-017, HBR-23, XSD-03 |
| C-11 | `days_of_week` theo ISO-8601: 1 = Thứ Hai, 7 = Chủ Nhật; thống nhất App/Server/tiến trình nền. | ☑️ | BQ-011, HBR-03 |
| MT-02 | Đầu việc chuẩn hóa thứ ISO, múi giờ VN và định danh lần uống ở Sprint 2. | ⏳ | — |

**Còn mở:**
*   ❓ Cách biểu diễn/truyền mốc thời gian UTC của `effective_from`/`ended_at` (BQ-013).
*   ❓ Cách cưỡng chế `doses_per_day` khớp số dòng lịch (HBR-22).

---

## 5. Xác nhận liều & trạng thái liều

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-01 | Cho xác nhận sớm tối đa **30 phút**. | ✅ | C-09, BQ-001 |
| QD-02 | Mốc tính là **giờ dự kiến uống**, không phải giờ thông báo hay giờ đồng bộ. | ✅ | BQ-002, SY-04 |
| QD-03 | `Δ = thời điểm uống hợp lệ − giờ dự kiến`: −30 ≤ Δ ≤ 30 phút → `da_uong`; 30 < Δ ≤ 120 phút → `uong_tre`; quá 120 phút chưa có xác nhận hợp lệ → `bo_lo`. | ✅ | BQ-003, HBR-02, XSD-01 |
| QD-10 | Bấm xác nhận thực sự sau 120 phút: vẫn ghi nhận riêng việc đã uống (lưu thời điểm thao tác, thời điểm uống khai báo, nguồn ghi nhận) nhưng kết quả tuân thủ giữ `bo_lo`; không tự coi khai báo hồi cứu là đúng giờ hay khuyến nghị uống bù. | ✅ | BQ-004 |
| QD-08 | Cho UPDATE theo nghiệp vụ và quyền từng bảng, gồm đối soát liều và kết thúc lịch cũ. | ✅ | CS-13 |
| QD-20 / C-18 | Tính năng chủ động hoãn liều vẫn hoãn (QD-20); xác nhận bằng giọng nói đã được đẩy sang giai đoạn 2 (hiện trạng ghi tại C-18). | ✅ | HBR-17, BQ-060 |
| BS-01 | Trạng thái liều chỉ gồm 3 giá trị `da_uong`, `uong_tre`, `bo_lo`; không thêm giá trị trạng thái mới. | 🆕 | C-09, Ch.10 |
| Ch.10 | Trạng thái liều truyền bằng mã chuẩn `da_uong`/`uong_tre`/`bo_lo`; chỉ đổi sang nhãn tiếng Việt trên giao diện. | ⏳ | — |

**Còn mở:** ❓ Chức năng "bỏ qua liều" trong SRS cũ chưa có quyết định riêng; phải được phân loại theo QD-46.

**Tiêu chí nghiệm thu biên (Ch.10):** Δ = −30 và +30 phút là `da_uong`; ngay trên +30 đến đúng +120 phút là `uong_tre`; vượt +120 phút giữ `bo_lo` và ghi nhận riêng; trước −30 phút không được xác nhận. Kiểm tra biên tới giây, không làm tròn.

> Đối soát ngoại tuyến, xung đột hai thiết bị, đồng hồ sai: xem [Mục 7](#7-ngoại-tuyến--đồng-bộ).

---

## 6. Nhắc thuốc & thông báo

### 6.1. Nhắc thuốc cho bệnh nhân

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-20 | Giai đoạn 1 tự nhắc lại **một lần sau 10 phút** cho liều chưa xác nhận/chưa hủy; kiểm tra trạng thái và khóa chống trùng trước khi nhắc. | ✅ | C-18, NT-04 |
| QD-21 | Gom thuốc cùng giờ thành một thông báo, mở danh sách xác nhận **từng thuốc**; chưa có nút "xác nhận tất cả". Hủy nhắc riêng liều đã xử lý; chỉ hủy cả nhóm khi không còn liều cần nhắc. | ✅ | NT-01, NT-05, BQ-018 |
| QD-22 | Ưu tiên lập các nhắc gần nhất trong hạn mức hệ điều hành (iOS 64), lấy 7 ngày làm **mục tiêu**, không phải điều kiện cắt cứng. Bổ sung khi mở app, sửa lịch, khi OS cho chạy nền; kết hợp push máy chủ có khóa chống trùng. Hiển thị thời điểm cuối đã lập nhắc và tình trạng quyền thông báo; không hứa nhắc vô hạn khi ngoại tuyến. | ✅ | NT-03 |
| QD-23 | Mở thông báo cũ → lấy trạng thái hiện tại: liều đã xác nhận/hủy chỉ hiển thị; quá 120 phút chỉ mở luồng ghi nhận riêng (QD-10). Ngoại tuyến dùng bản lưu có nhãn "chưa cập nhật", lưu thao tác chờ kiểm tra phiên bản khi đồng bộ. | ✅ | BQ-019, NT-11 |
| QD-26 | Màn hình khóa chỉ hiện nội dung chung. Giờ yên lặng mặc định áp dụng cho thông báo phụ/người thân; muốn tắt tiếng nhắc uống thuốc phải chọn riêng, vẫn giữ giờ dự kiến, không phát lại nhắc đã hết hạn. | ✅ | NT-02, NT-08, BQ-023, CS-14 |
| QD-26 | Hộp thư thông báo tự xóa nội dung sau 30 ngày; không xóa lịch sử liều hay audit. | ✅ | NT-12 |
| NT-06 | Android: lắng nghe `BOOT_COMPLETED` để tự đặt lại toàn bộ nhắc sau khởi động. | ⏳ | — |
| NT-07 | Hiển thị biểu ngữ cảnh báo ở màn hình chính khi mất quyền thông báo/hẹn giờ chính xác. | ⏳ | — |
| MT-09 | Ma trận kiểm thử thông báo trên các hãng Android (Samsung, Xiaomi, Oppo…). | ⏳ | — |

### 6.2. Cảnh báo cho người thân

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-25 | Quét liều vừa vượt 120 phút tối đa mỗi **60 giây**. SLO: p95 ≤ **2 giây** từ commit giao dịch phát hiện bỏ lỡ đến khi FCM chấp nhận, tính cả thời gian chờ queue; tại tải nghiệm thu, khi FCM hoạt động. Không cam kết thời gian thiết bị hiển thị. Báo cáo riêng độ trễ phát hiện, tỷ lệ lỗi, gián đoạn. Queue/worker thông báo ưu tiên, tách khỏi OCR/LLM. | ✅ | BQ-021, NT-09, NT-10 |
| QD-24 | Gửi đính chính khi đối soát đổi kết quả `bo_lo`, chỉ cho người thân từng được gửi cảnh báo tương ứng và hiện còn đủ quyền; cập nhật hộp thư; chống trùng theo liều + phiên bản kết quả + người nhận; kiểm tra quyền lần cuối ngay trước gửi. | ✅ | SY-17, BQ-020 |
| QD-28 | Gửi cảnh báo cần đủ điều kiện chia sẻ (xem Mục 8). | ✅ | NT-09 |

### 6.3. Phạm vi nền tảng

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| C-06 | Chấp nhận giảm phạm vi iOS (Free Apple ID, cài qua Mac, không APNs); kiểm thử đầy đủ thông báo trên Android/FCM. | ☑️ | biên bản mục 3 |
| C-07 | Người thân dùng iPhone chỉ thấy cập nhật hộp thư khi tự mở app. Push bổ sung và SLO FCM chỉ áp dụng nơi có push. | ☑️ | HBR-12 |
| MT-10 | Đính chính tiêu chí nghiệm thu cảnh báo người thân theo iOS/Android. | ⏳ | — |
| BS-03 | Không mua tài khoản Apple Developer/APNs. Trên iOS chấp nhận hộp thư trong app cập nhật trễ và không áp yêu cầu thời gian thực; đóng BQ-022 theo C-06/C-07. | 🆕 | BQ-022, C-06, C-07, HBR-12 |

**Còn mở:** ❓ Cấu trúc ID thông báo cục bộ, cơ chế tránh va chạm, TTL thông báo đẩy (BQ-020).

---

## 7. Ngoại tuyến & đồng bộ

### 7.1. Đối soát dữ liệu liều

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-11 | Tự động đối soát trong **14 ngày** tính từ giờ dự kiến của liều tới lần máy chủ tiếp nhận bền vững đầu tiên; thời gian chờ queue không làm bản ghi quá hạn. Quá hạn vẫn nhận vào hồ sơ bằng chứng chờ đối soát, không tự đổi kết quả, không xóa. | ✅ | SY-01, SY-15, BQ-005 |
| QD-12 | Thời điểm bất hợp lý → giữ ở trạng thái chờ đối soát, không tự sửa bằng độ lệch cũ, không tự tính tuân thủ. Lưu giờ thiết bị gốc, giờ nhận máy chủ, mốc đồng bộ giờ gần nhất, khoảng thời gian đơn điệu nếu có. | ✅ | BQ-016, SY-04, XSD-03 |
| QD-13 | Hai xác nhận khác giờ cho cùng liều → xung đột: giữ cả hai bằng chứng, yêu cầu bệnh nhân xác nhận thời điểm thực tế; mỗi liều chỉ một kết quả hiệu lực; mọi hiệu chỉnh có audit; báo cáo đánh dấu "đang đối soát", không chọn theo thứ tự đến. | ✅ | BQ-008, SY-03 |
| QD-14 | Cùng tài khoản + UUID + cùng nội dung → trả lại kết quả cũ; khác nội dung → `409`, giữ bản đã lưu. Sửa nội dung dùng yêu cầu hiệu chỉnh UUID mới, tham chiếu bản gốc, phiên bản và lý do (kể cả sửa bản từng bị từ chối). | ✅ | BQ-009, BQ-056, SY-02, SY-14 |

### 7.2. Gửi mẻ, thử lại & lỗi

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-07 | Mỗi liều trong mẻ xử lý độc lập. Mất mạng/timeout/408/429/5xx → thử lại có giãn cách, tôn trọng thời gian chờ máy chủ. 400/422 → giữ bản lỗi, chỉ gửi lại khi đã xử lý nguyên nhân. 403 → dừng tự gửi, giải quyết quyền. 409 → đối soát, không gửi lặp mù. Giữ nguyên UUID và nội dung khi thử lại. | ✅ | C-20, BQ-053, SY-05, SY-07 |
| QD-06 | 401 → làm mới token một lần; thành công thì gửi lại một lần. Refresh hết hạn/bị thu hồi hoặc vẫn 401 → dừng đồng bộ, giữ dữ liệu, yêu cầu đăng nhập lại **đúng tài khoản**. Refresh lỗi do mạng/máy chủ → chờ thử lại, không xóa dữ liệu. | ✅ | BQ-054, SY-06 |
| QD-18 | Tối đa **50 bản ghi/mẻ**, một mẻ đang gửi/thiết bị, trả kết quả từng bản. Backoff exponential + full jitter từ 2 giây tới trần 5 phút; tôn trọng `Retry-After`; ngẫu nhiên hóa lần gửi đầu sau khi nối mạng. | ✅ | SY-11, BQ-053 |
| QD-18 | API chỉ ACK sau khi lưu CSDL + outbox trong cùng giao dịch; RabbitMQ + Celery xử lý idempotent, retry hữu hạn rồi cách ly lỗi; Redis chỉ là cache dựng lại được. | ✅ | HBR-24 |
| Ch.10 | Gửi mẻ 10 liều lỗi 1: lưu bền vững 9 liều hợp lệ, trả kết quả từng liều **và** tổng số. | ✅ | C-20 |

### 7.3. Tải dữ liệu xuống máy

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-18 | Tải phân trang toàn bộ định nghĩa lịch đang hiệu lực và lịch tương lai đã tạo, kèm lịch sử 30 ngày; không dựng vô hạn các liều tương lai. | ✅ | SY-12 |

### 7.4. Đăng xuất, đổi máy & dữ liệu cục bộ

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-05 | Không cho đăng xuất hoặc đổi tài khoản khi còn dữ liệu chưa đồng bộ; bản ghi đang lỗi vẫn tính là chưa đồng bộ. | ✅ | SY-08, CS-12 |
| QD-17 | Sửa lỗi qua luồng hiệu chỉnh hoặc gửi hỗ trợ; không cho tự hủy dữ liệu để vượt chặn. Máy chủ có luồng nhận bằng chứng lỗi vào kho bền vững kèm mã biên nhận; chỉ hết chặn khi mọi bản ghi đã được nhận an toàn (dù đối soát còn chờ). Chưa có biên nhận → giữ bản cục bộ. | ✅ | BQ-055 |
| QD-19 | Giai đoạn 1 chấp nhận không khôi phục được dữ liệu chỉ có trên máy nếu xóa app/mất máy trước khi đồng bộ; chưa có sao lưu đám mây riêng. Cung cấp số bản đang chờ, nút đồng bộ, hướng dẫn hoàn tất trước khi chuyển máy. Hàng đợi cục bộ phải lưu bền vững và bảo vệ theo tài khoản. | ✅ | MT-12, BQ-064 |
| SY-13 | Bắt buộc mã hóa CSDL cục bộ (SQLCipher hoặc bảo vệ của OS). | ⏳ | HBR-20 |
| SY-16 | Hiển thị trạng thái "đang chờ đồng bộ" (đồng hồ cát) → "đã lưu máy chủ" (tích xanh). | ⏳ | — |

**Còn mở:**
*   ❓ Số lần tự thử lại tối đa của client/worker; mục tiêu đồng bộ ≤30 giây (QA.08) không phải bảo đảm khi đang backoff (BQ-054).
*   ❓ Vòng đời mã thiết bị, khóa mã hóa cục bộ, thao tác thu hồi/xóa khóa (BQ-064).

---

## 8. Người thân: liên kết & chia sẻ

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-04 | Mỗi người dùng có **một mã cố định, không hết hạn**. Nhập mã chỉ tạo yêu cầu; **bệnh nhân phải chấp thuận** mới liên kết thành công. | ✅ | C-19, BQ-024, BQ-025, HBR-10 |
| QD-34 | Mã gồm 10 ký tự ngẫu nhiên chữ/số dễ phân biệt, kèm QR. Phải đăng nhập mới gửi yêu cầu; phản hồi tra cứu không lộ hồ sơ. | ✅ | CS-11 |
| QD-34 | Chống dò mã: sai 5 lần/15 phút → khóa bên gửi 15 phút, kết hợp giới hạn IP/thiết bị; tối đa 10 yêu cầu/ngày/tài khoản; 1 yêu cầu đang chờ/cặp; chờ 24 giờ sau khi bị từ chối (*thay bằng BS-04, PM chốt 14/10/2026*); phía bệnh nhân gộp tối đa 5 thông báo yêu cầu/giờ. Không khóa tài khoản bệnh nhân vì lưu lượng từ người lạ. | ✅ | CS-11, BS-04 |
| BS-04 | Bị từ chối thì người thân gửi lại yêu cầu được ngay. Cùng một bệnh nhân từ chối cùng một người thân **5 lần liên tiếp** thì người thân bị chặn gửi lại cho bệnh nhân đó **24 giờ** tính từ lần từ chối thứ 5; hết 24 giờ, hoặc khi bệnh nhân chấp thuận một yêu cầu của cặp, bộ đếm về 0. Bị hủy liên kết không tính. Thay phần "chờ 24 giờ sau khi bị từ chối" của QD-34 (PM chốt 14/10/2026, task 3.13). | 🆕 | QD-34, QD-30 |
| BS-05 | Phải đồng ý `family_sharing` mới lấy và chia sẻ được mã liên kết. Chưa đồng ý hoặc đã rút thì mã của người đó coi như không tồn tại với người nhập (không lộ trạng thái đồng ý); đồng ý lại thì mã cũ dùng lại được (chốt 14/10/2026, task 3.13). | 🆕 | QD-04, QD-28, QD-34 |
| QD-27 | Giai đoạn 1 người thân **chỉ xem** dữ liệu được chia sẻ và nhận cảnh báo; không thêm/sửa thuốc, sửa lịch, xác nhận hộ. | ✅ | CS-06, BQ-026 |
| QD-28 | Mọi lần chia sẻ phải đồng thời có: liên kết hoạt động + bật chia sẻ + đồng ý `family_sharing` còn hiệu lực. Tạo/xem gợi ý món ăn qua vai trò người thân cần thêm `ai_meal` còn hiệu lực và phạm vi tương ứng. Backend kiểm tra theo chủ thể dữ liệu ở mỗi yêu cầu và mỗi tác vụ gửi. | ✅ | CS-02, BQ-026, BQ-047 |
| QD-29 | Không lưu ngoại tuyến dữ liệu sức khỏe của người thân; chỉ giữ bộ nhớ phiên, xóa khi mất mạng, vào nền, đăng xuất hoặc phát hiện thu hồi. | ✅ | BQ-028, CS-03 |
| QD-29 | Kiểm tra quyền tại CSDL trước khi trả dữ liệu và trước khi gửi thông báo; khi thu hồi: vô hiệu cache, chặn tác vụ chưa gửi. Không hứa thu hồi thông báo đã giao/ảnh chụp màn hình → chỉ gửi nội dung chung. | ✅ | BQ-027, XSD-06 |
| QD-30 | Hủy rồi liên kết lại phải tạo yêu cầu mới, bệnh nhân xác nhận lại; giữ lịch sử liên kết cũ; không tự khôi phục phạm vi chia sẻ cũ. | ✅ | BQ-029, CS-08 |

**Còn mở:**
*   ❓ Ma trận endpoint/mục đích đầy đủ cho người thân; không suy ra phạm vi `health_data` ngoài bản chốt (HBR-18).
*   ❓ Danh sách loại đồng ý (3 loại cố định) có thể chưa bao quát OCR, phân tích, thông báo (HBR-21).

---

## 9. Đồng ý, kiểm toán & phân quyền

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-31 | Lịch sử đồng ý là chuỗi sự kiện **chỉ thêm mới** (đồng ý/rút lại, chủ thể, phạm vi, phiên bản nội dung, thời điểm máy chủ); trạng thái hiện tại suy ra hoặc lưu ở bảng tổng hợp riêng; cấm sửa/ẩn dòng cũ bằng nghiệp vụ thông thường. | ✅ | C-15, CS-10 |
| QD-08 | Quyền UPDATE theo nghiệp vụ không tự bỏ quy tắc chống sửa nhật ký kiểm toán và lịch sử đồng ý. | ✅ | C-16, CS-09, MT-11 |
| QD-33 | Ghi audit cho truy cập của bệnh nhân, người thân, admin, lượt bị từ chối, tác vụ nền và xuất dữ liệu; chỉ metadata tối thiểu, không chép nội dung y tế vào log. | ✅ | BQ-031, CS-05, HBR-14 |
| QD-33 | Tiếp tục khi sự kiện đã vào kho audit/outbox bền vững dù bộ xử lý log lỗi. Không ghi bền vững được → máy chủ chặn đọc/chia sẻ/xuất và không ACK ghi mới; app vẫn nhắc và xác nhận cục bộ để đồng bộ sau. Sự kiện xem ngoại tuyến lưu cục bộ, gửi khi có mạng. | ✅ | BQ-032, XSD-11 |
| QD-32 | Giai đoạn 1 **không** có quyền admin vượt đồng ý để truy cập y tế khẩn cấp. Admin vận hành chỉ xem dữ liệu kỹ thuật tối thiểu theo quyền, không sửa lịch sử uống thuốc; hỗ trợ đối soát qua luồng có bệnh nhân xác nhận và audit. | ✅ | BQ-030, CS-07 |
| CS-01 | 100% API y tế đi qua PEP, kiểm tra quyền từng request. | ⏳ | LDR-03 |
| CS-04 | Truy cập trái phép → 403 không lộ thông tin, ghi log vi phạm ở transaction riêng. | ⏳ | BQ-032 |

**Còn mở:**
*   ❓ Vị trí ghi audit/outbox cụ thể; log lượt bị từ chối không mất khi giao dịch nghiệp vụ rollback (BQ-032).
*   ❓ Thời hạn lưu audit khi tài khoản còn hoạt động; quyền xem/xuất audit chi tiết (BQ-033).

---

## 10. Xóa tài khoản & lưu giữ dữ liệu

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-35 | Bệnh nhân xác thực lại để yêu cầu xóa; có **7 ngày** để hủy. Ngay khi yêu cầu: ngừng chia sẻ và xử lý AI; dữ liệu chưa đồng bộ phải giải quyết theo QD-05/QD-17 trước khi hoàn tất. | ✅ | BQ-034, BQ-035, MT-06 |
| QD-35 | Hết hạn hủy: tự động xóa hồ sơ, lịch/liều, liên kết, ảnh OCR, token, cache. Chỉ giữ audit/đồng ý tối thiểu đã tách định danh trong **90 ngày** rồi xóa. Backup mã hóa luân chuyển tối đa **30 ngày**; phục hồi backup phải áp dụng lại danh sách xóa. | ✅ | BQ-033, XSD-10, LDR-06 |
| QD-35 | Celery xử lý từng bước idempotent, retry hữu hạn rồi chuyển hỗ trợ; chỉ báo hoàn tất sau kiểm chứng. Người phụ trách dữ liệu chịu trách nhiệm vận hành. Đây là chính sách sản phẩm, không phải thời hạn luật định; ngoại lệ lưu giữ phải có căn cứ và phạm vi riêng. | ✅ | BQ-036, BQ-037 |
| QD-26 | Xóa hộp thư thông báo (30 ngày) không xóa lịch sử liều hay audit. | ✅ | NT-12 |

**Còn mở:**
*   ❓ Loại yêu cầu được mở đồng thời; điều kiện gửi lại sau từ chối (BQ-035).
*   ❓ Quy trình khiếu nại, mã lý do từ chối, xử lý ngoại lệ lưu giữ (BQ-036).
*   ❓ Số lần retry tối đa và thời điểm thông báo từng trạng thái lỗi (BQ-037).

---

## 11. Tương tác thuốc & gợi ý món ăn

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-37 | Dược sĩ phụ trách kiểm duyệt nội dung → người có chuyên môn độc lập duyệt → người quản lý danh mục phát hành phiên bản có nguồn và ngày cập nhật. Thiếu vai trò duyệt thì chưa phát hành quy tắc mới. | ✅ | BQ-040, MT-08, XSD-09 |
| QD-37 | Kết quả ba trạng thái tách rõ: "chưa đủ dữ liệu", "có tương tác", "đã kiểm tra, chưa thấy tương tác trong phạm vi dữ liệu hiện có". | ✅ | BQ-041, LDR-05 |
| QD-40 | Dị ứng và hạn chế ăn uống là **bắt buộc**, cho khai "không có" hoặc "chưa biết"; sở thích là tùy chọn. Thiếu/chưa biết → hỏi bổ sung, chưa tạo gợi ý cá nhân hóa; nhắc thuốc vẫn hoạt động bình thường. Chỉ yêu cầu thông tin khi dùng tính năng. | ✅ | BQ-045 |
| QD-41 | Giai đoạn 1 **tắt** gửi dữ liệu sức khỏe tới LLM bên ngoài, hoãn chọn nhà cung cấp; chỉ dùng mẫu món ăn đã kiểm duyệt + bộ kiểm tra quy tắc. | ✅ | BQ-046, HBR-19, LDR-08 |
| QD-41 | Nếu mở tích hợp sau: chỉ gửi hoạt chất, dị ứng, hạn chế ăn uống, sở thích cần thiết sau `ai_meal`; không gửi định danh/đơn thuốc thô; nhà cung cấp không huấn luyện từ dữ liệu, không lưu payload. | ✅ | XSD-13 |
| QD-41 | Redis cache riêng theo tài khoản tối đa 24 giờ, vô hiệu khi dữ liệu/đồng ý đổi; luôn kiểm tra lại quy tắc hiện hành trước khi hiển thị. | ✅ | BQ-048 |
| QD-28 | Người thân tạo/xem gợi ý món ăn cần thêm `ai_meal` (xem Mục 8). | ✅ | BQ-047 |

**Còn mở:** ❓ Chỉ số độ đa dạng N của kết quả món ăn; không suy ra N từ TTL cache (BQ-048).

---

## 12. Báo cáo tuân thủ

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-42 | Tỷ lệ tuân thủ = (`da_uong` + `uong_tre`) / số liều **không bị hủy và đã vượt cửa sổ 120 phút**; tử số chỉ lấy trong tập mẫu số. Hiển thị tỷ lệ đúng giờ riêng. | ✅ | BQ-050, MT-15, XSD-01 |
| QD-42 | Không có liều đủ điều kiện → "không có dữ liệu"; liều đang trong cửa sổ → "đang chờ". Bằng chứng sau 120 phút (QD-10) không vào tử số. Liều xung đột vẫn ở mẫu số, chưa vào tử số; báo cáo gắn nhãn tạm thời. | ✅ | HBR-24, LDR-01 |
| QD-42 | Đối soát hợp lệ phải tính lại báo cáo, lưu thời điểm/phiên bản cập nhật. | ✅ | — |

---

## 13. Chế độ đơn giản

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-43 | Lưu chế độ đơn giản theo tài khoản trên máy chủ + cache trên máy; đổi khi ngoại tuyến có hiệu lực ngay, đồng bộ bằng phiên bản khi có mạng, phục hồi trên máy mới. Xung đột tùy chọn giao diện không được chặn đồng bộ liều uống. | ✅ | BQ-049, LDR-10, MT-16 |

---

## 14. Hợp đồng API & dữ liệu

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| C-14 | Mã lịch uống thuốc thống nhất kiểu `bigint` trên CSDL, API và Mobile. | ☑️ | HBR-20, biên bản mục 5 |
| C-21 | 100% tên trường JSON API bằng tiếng Anh. | ☑️ | Ch.10 |
| C-08 / C-24 | Schema v11 là gốc duy nhất; code và API cập nhật theo v11; bỏ tham chiếu Schema v2. | ☑️ | — |
| QD-45 | API chuẩn chỉ định tại `DrugTime/api_contract/openapi.json`; bản generated chỉ để đối chiếu. Tech Lead quản lý API. | ✅ | C-13, BQ-061 |
| Ch.10 / MT-03 | Endpoint gửi liều: `/api/v1/dose-logs/batch-sync`. | ⏳ | — |

**Còn mở:** ❓ `openapi.json` chưa có trong checkout khi chốt; tiền tố/endpoint chi tiết phải đối chiếu bản chuẩn trước nghiệm thu (BQ-061).

---

## 15. Hạ tầng & kiến trúc nền

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-09 | RabbitMQ + Celery cho hàng đợi/tác vụ nền; Redis chỉ làm cache; bỏ Redis + RQ cho queue. | ✅ | C-12, BQ-059, MT-14, LDR-12 |
| C-03 | Triển khai trên Render; bỏ Oracle VM và Caddy. | ☑️ | XSD-13 |
| QD-25 | Queue/worker thông báo ưu tiên, tách khỏi OCR/LLM. | ✅ | NT-10 |

**Còn mở:** ❓ Điều kiện nhà cung cấp/vùng lưu trữ và hồ sơ DPIA của Render, Supabase, FCM chưa được kiểm chứng (XSD-13, LDR-08).

---

## 16. Quản trị phạm vi, tài liệu & nghiệm thu

| Mã | Quyết định | TT | Mã liên quan |
|---|---|---|---|
| QD-45 | Backlog chuẩn: `DrugTime/docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx`. Sổ quyết định: `drugtime_quyet_dinh_va_cau_hoi_can_chot.md`, baseline `QD-2026-10-03-v1`. | ✅ | C-02, C-04, MT-13, XSD-15 |
| QD-45 | PM quản lý Backlog/sổ quyết định; Tech Lead quản lý API; QA lập ánh xạ yêu cầu–kiểm thử, lưu commit/hash từng bản trong manifest phát hành. | ✅ | BQ-063 |
| QD-45 | Ngoại lệ chỉ được PO + Tech Lead chấp nhận, có đánh giá QA; rủi ro y tế cần người duyệt chuyên môn; không miễn trừ lỗi mất/sai dữ liệu y tế hoặc truy cập trái quyền. | ✅ | BQ-065 |
| QD-46 | Hoãn tính năng nhà thuốc sang giai đoạn sau, không xóa khỏi yêu cầu. Mọi SRS chưa ánh xạ phải có chủ sở hữu và được phân loại trước nghiệm thu. | ✅ | BQ-060, HBR-17 |
| QD-46 | Yêu cầu thuộc luồng cốt lõi, an toàn, bảo mật hoặc QD-10–45 phải vào Backlog giai đoạn 1; phần ngoài phạm vi ghi rõ hoãn và lý do. Chỉ nghiệm thu khi có ma trận phạm vi và tiêu chí kiểm thử cho mọi mục giai đoạn 1. | ✅ | LDR-11 |
| C-05 | Phạm vi kiểm thử chấp nhận PB43: tới Sprint 6. | ☑️ | LDR-11 |
| C-22 | Đề cương chính thức: bản PDF v5 (hoặc bản Mentor ký gần nhất). | ☑️ | — |
| C-23 | Loại file rác/lỗi/nhầm dự án khỏi danh mục thẩm định. | ☑️ | — |
| C-25 | Task 2.25 (Engine đồng bộ Mobile) thuộc Sprint 2. | ☑️ | — |
| C-26 | Ước lượng task 2.12 lấy theo Excel (4 giờ). | ☑️ | — |

**Còn mở:**
*   ❓ Manifest phiên bản và ánh xạ PB–Sprint cụ thể khi phát hành (BQ-058).
*   ❓ Ánh xạ D1–D13 với CD chưa xác minh (BQ-062).
*   ❓ Phân công người cụ thể và người duyệt chuyên môn (BQ-063).
*   ❓ Danh sách lỗi Nghiêm trọng/Cao còn mở và bằng chứng đóng lỗi (BQ-065).

---

## 17. Điểm không nhất quán phát hiện khi gom nhóm

| # | Vấn đề | Vị trí | Đề xuất xử lý |
|---|---|---|---|
| 1 | CSDL/hợp đồng chỉ có 3 trạng thái liều (`da_uong`, `uong_tre`, `bo_lo`), nhưng các quyết định cần thêm khái niệm **liều đã hủy** (QD-16, QD-20, QD-21, QD-23, QD-42), **chờ đối soát/xung đột** (QD-11–13, QD-42) và **bằng chứng ghi nhận sau 120 phút** (QD-10). | C-09, C-18, Ch.10 ↔ QD-10–16, QD-42 | ✅ **Đã xử lý (BS-01):** giữ 3 trạng thái. Hệ quả: liều hủy, chờ đối soát/xung đột và bằng chứng sau 120 phút không phải giá trị trạng thái liều; cần đặc tả cách biểu diễn (cột/bảng phụ) trong Schema v11. |
| 2 | QD-15 yêu cầu mỗi dòng lịch có **múi giờ**, trong khi C-10/HBR-23 nói CSDL không lưu timezone và cố định VN. | QD-15 ↔ C-10, HBR-23 | ✅ **Đã xử lý (BS-02):** chỉ một múi giờ Việt Nam, không lưu theo dòng lịch. |
| 3 | Kiểu mã lịch: C-14 ghi `bigint`; Ch.10 và biên bản mục 5 ghi "số nguyên (int)". | C-14 ↔ Ch.10, Ch.11 | Ghi thống nhất là số nguyên 64-bit (`bigint`/int64). |
| 4 | BQ-022 vẫn chờ duyệt và còn phương án "mua tài khoản hỗ trợ APNs", mâu thuẫn với C-06/C-07 đã "Đồng ý". | BQ-022 ↔ C-06, C-07 | ✅ **Đã xử lý (BS-03):** không mua APNs, đóng BQ-022 theo C-06/C-07. |
| 5 | HBR-03 ghi "CÒN THIẾU QUY TẮC", HBR-20 ghi "XUNG ĐỘT", HBR-12 ghi "XUNG ĐỘT" — đều đã có quyết định (C-11, C-14, C-06/C-07). | Chương 3 | Cập nhật cột xử lý của HBR-03/12/20 trỏ về quyết định tương ứng. |
| 6 | BQ-032 dựa vào CS-04 ("ghi log từ chối ở transaction riêng") như đã chốt, nhưng CS-04 còn ⏳. | BQ-032 ↔ CS-04 | Duyệt CS-04 cùng lúc với đặc tả BQ-032. |
| 7 | SY-13 (mã hóa CSDL cục bộ) còn ⏳, trong khi HBR-20 ghi app đã dùng SQLCipher và QD-19 yêu cầu hàng đợi cục bộ "bảo vệ theo tài khoản". | SY-13 ↔ HBR-20, QD-19 | Chốt SY-13 để QD-19 có căn cứ bảo vệ cụ thể. |
| 8 | MT-02, MT-03 còn ⏳ dù nội dung đã được C-10, C-11, C-14, C-21 quyết định; riêng endpoint `batch-sync` chưa có quyết định nào khác ngoài Ch.10. | Chương 9 ↔ Chương 1 | Duyệt MT-02; duyệt riêng endpoint trong MT-03 sau khi có `openapi.json`. |

---

## 18. Bảng tra QD → chức năng

| QD | Chức năng | QD | Chức năng | QD | Chức năng |
|---|---|---|---|---|---|
| 01 | 5 | 17 | 7 | 33 | 9 |
| 02 | 5 | 18 | 7 | 34 | 8 |
| 03 | 5 | 19 | 7 | 35 | 10 |
| 04 | 8 | 20 | 6 | 36 | 2 |
| 05 | 7 | 21 | 6 | 37 | 11 |
| 06 | 7 | 22 | 6 | 38 | 2 |
| 07 | 7 | 23 | 6 | 39 | 3 |
| 08 | 5, 9 | 24 | 6 | 40 | 11 |
| 09 | 15 | 25 | 6, 15 | 41 | 11 |
| 10 | 5 | 26 | 6, 10 | 42 | 12 |
| 11 | 7 | 27 | 8 | 43 | 13 |
| 12 | 7 | 28 | 8, 6, 11 | 44 | 1 |
| 13 | 7 | 29 | 8 | 45 | 14, 16 |
| 14 | 7 | 30 | 8 | 46 | 16 |
| 15 | 4 | 31 | 9 | | |
| 16 | 4 | 32 | 9 | | |
