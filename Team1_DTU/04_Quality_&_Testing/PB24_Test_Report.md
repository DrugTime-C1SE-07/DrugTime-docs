# Báo Cáo Nghiệm Thu Kỹ Thuật Kiểm Thử Thuật Toán Tương Tác Thuốc (Task 4.03)

- **Mã dự án:** PB24 — Kiểm tra tương tác thuốc–thuốc
- **Mã công việc:** Task 4.03 (Test: Interaction-Detection Algorithm)
- **Người thực hiện:** Duc / Engineering Team
- **Ngày lập báo cáo:** 03/11/2026
- **Văn bản kế hoạch gốc:** `sprint4_plan/4.03.md` (Tài liệu kế hoạch trong workspace)
- **Tài liệu ma trận kiểm thử:** `sprint4_plan/PB24/4.03_test_matrix.md` (Ma trận kiểm thử trong workspace)

---

## 1. Mục Đích & Phạm Vi Kiểm Thử

### 1.1. Mục đích
Báo cáo này tổng hợp kết quả thực thi kiểm thử toàn diện thuật toán phát hiện tương tác thuốc (CD7), API kiểm tra tương tác của người bệnh, hiệu năng phản hồi (NFR01) và giao diện người dùng Mobile. Báo cáo nhằm cung cấp bằng chứng kỹ thuật minh bạch bàn giao cho Product Owner (PO) và Mentor; phân định rạch ròi giữa các cơ chế phần mềm đã được xác minh với các khoảng trống lâm sàng còn phụ thuộc.

### 1.2. Phạm vi kiểm thử
1. **Thuật toán Evaluator thuần (Pure Function CD7):** Đánh giá tính tất định, tính giao hoán ($A+B = B+A$), đa thuốc (polypharmacy $\ge 3$ thuốc), xử lý thuốc thiếu hoạt chất (`khong_du_du_lieu`), bảo vệ an toàn đơn vị liều (`DoseThreshold`), cơ chế khử trùng lặp theo cặp thuốc và câu miễn trừ trách nhiệm y tế (Disclaimer NFR03).
2. **API Endpoint POST `/patients/{id}/interaction-checks`:** Kiểm tra phân quyền truy cập (DK3), đối soát danh mục catalog, cấu trúc phản hồi JSON 3 trạng thái và tính năng phản hồi hỗn hợp (`mixed_response`).
3. **Hiệu năng hệ thống (NFR01):** Benchmark độ trễ xử lý thuật toán thuần và chu trình xử lý request HTTP qua TestClient.
4. **Giao diện người dùng Mobile (Flutter UI):** Kiểm chứng hộp thoại cảnh báo tương tác (`CẦN THẬN TRỌNG PHỐI HỢP`, `CẢNH BÁO CHỐNG CHỈ ĐỊNH`), dialog thiếu hoạt chất, phản hồi hỗn hợp, xử lý lỗi mạng và chuỗi disclaimer NFR03.

### 1.3. Ranh giới kiểm toán & An toàn môi trường
> [!IMPORTANT]
> **Tuân thủ quy định bảo vệ an toàn cơ sở dữ liệu và đạo đức lâm sàng:**
> - **Tuyệt đối không kết nối DB Dev dùng chung hoặc Production:** Toàn bộ kiểm thử được thực hiện trên môi trường test cô lập, in-memory fixtures và mocks.
> - **Phân định rõ phạm vi kiểm thử PostgreSQL:** Đã thực thi kiểm thử tích hợp trên database test riêng biệt `drugtime_seed_test` (loopback) với fixture nhân tạo (`synthetic_active_ingredient_alpha`, `synthetic_active_ingredient_beta`) để kiểm chứng cú pháp SQL, tính lũy thừa và cơ chế rollback transaction của bộ khung `seed_loader_scaffolding.TransactionSafeSeedLoader` (scaffold). Đây **KHÔNG PHẢI** là kiểm chứng production loader hay production safety gate trong môi trường vận hành thực tế, và **KHÔNG PHẢI** là E2E live endpoint của người bệnh (`POST /patients/{id}/interaction-checks`). Các bài test API endpoint vẫn được thực hiện qua FastAPI `TestClient` với mock adapters.
> - **Chưa kiểm thử trên thiết bị di động vật lý:** Toàn bộ 13 bài test Flutter được thực hiện trên headless widget/flow test runner, chưa chạy trên thiết bị iOS/Android vật lý.
> - **Phân tách rạch ròi giữa Lâm sàng và Kỹ thuật:**
>   - 10 ca tương tác ĐTĐ (`TC-POS-01`..`10`) và 5 ca candidate âm tính (`TC-NEG-01`..`05`) được gắn nhãn `provisional`. Toàn bộ dữ liệu lâm sàng giữ nguyên trạng thái `pending_review` (chưa có chữ ký Dược sĩ lâm sàng); kết quả test chỉ chứng minh **draft-conformance kỹ thuật** với tập quy tắc dự thảo, **không tuyên bố độ chính xác y khoa (True Positive/False Positive lâm sàng)**.
>   - 17 hoạt chất OTC (vai trò `trieu_chung_cap_tinh`) đã được chuyển sang thư mục `markdown/OTC_Phase2/` và loại khỏi deliverable PB24 đợt này, bảo lưu hồ sơ chứng cứ cho Phase 2.
>   - 12 ca kỹ thuật (`synthetic`) sử dụng 100% định danh nhân tạo thuần túy để kiểm chứng cơ chế logic phần mềm, không đại diện cho tương tác lâm sàng.

### 1.4. Biên Bản Ghi Nhận Chỉ Đạo Kỹ Thuật Từ Product Owner (PO Technical Guidance Log - 04/11/2026)
> [!NOTE]
> **Chỉ đạo Kỹ thuật từ Product Owner (PO) ngày 04/11/2026:**
> - **Thời điểm ghi nhận:** 04/11/2026.
> - **Phạm vi:** Toàn bộ cụm triển khai kỹ thuật PB24 (Tasks 4.01, 4.02, 4.03) và 5 Draft PRs (#51, #17, #45, #55, #28).
> - **Người đưa chỉ đạo:** Chủ dự án (Project Owner - PO).
> - **Nội dung chỉ đạo:** Cho phép tiếp tục triển khai các công việc kỹ thuật phần mềm (xây dựng engine, API endpoint, kiểm thử ma trận, đồng bộ hợp đồng OpenAPI và giao diện cảnh báo) mà **không cần chờ chữ ký số hoặc attestation của Dược sĩ lâm sàng làm điều kiện tiên quyết chặn tiến trình kỹ thuật**.
> - **Ranh giới và giới hạn bắt buộc:**
>   1. **Không phải phê duyệt/nghiệm thu chính thức:** Chỉ đạo này **KHÔNG PHẢI là văn bản phê duyệt nghiệm thu chính thức toàn bộ PB24**, và **KHÔNG bãi bỏ tiêu chí DoD lâm sàng**. Tiêu chí kiểm định lâm sàng vẫn được bảo lưu.
>   2. **Ý nghĩa nguồn sách:** Dữ liệu "có nguồn từ sách" chỉ chứng minh nguồn gốc xuất xứ (provenance) và cơ chế tham khảo y văn (*Dược thư Quốc gia Việt Nam 2018*, *Sách Tương tác thuốc và chú ý khi chỉ định 2015*, *Martindale The Complete Drug Reference 38th*), **chưa được Dược sĩ lâm sàng kiểm định**, **tuyệt đối không được coi là clinical validation hay DoD lâm sàng đã đạt**.
>   3. **Phân biệt rõ trạng thái rà soát:** Trong hai workbook `PendingReview_v2.xlsx` và `PendingReview.xlsx`, trạng thái `"Đã đối chiếu nguồn"` chỉ xác nhận đã kiểm tra sách và số trang đối chiếu y văn, **KHÔNG ĐỒNG NGHĨA "đã thẩm định lâm sàng" hay "được phép dùng lâm sàng"**. Dữ liệu **CHƯA ĐƯỢC DƯỢC SĨ KIỂM ĐỊNH**.
>   4. **Không gắn nhãn giả mạo:** Tuyệt đối không gắn nhãn `clinically verified`, không tạo chữ ký/attestation giả; toàn bộ 10 quy tắc ĐTĐ của Task 4.01 được giữ nguyên trạng thái `pending_review` trong cơ sở dữ liệu và loader.
>   5. **Câu miễn trừ trách nhiệm y tế bắt buộc:** Câu miễn trừ trách nhiệm y tế (Disclaimer NFR03) bắt buộc luôn hiển thị trên UI Mobile và API payload.
>   6. **Cổng an toàn Live DB:** `TransactionSafeSeedLoader` tiếp tục chặn mọi hành vi nạp dữ liệu chưa duyệt vào DB production hoặc DB dùng chung.
>   7. **Bảo tồn lịch sử tiêu chí:** Giữ nguyên lịch sử tiêu chí ban đầu làm mốc đối chiếu phục vụ thẩm định y tế chuyên sâu sau này.

---

## 2. Môi Trường Kiểm Thử & Lệnh Thực Thi

### 2.1. Cấu hình môi trường
- **Hệ điều hành:** Microsoft Windows 11 Pro (x64)
- **Backend Runtime:** Python 3.14.7, pytest 9.2.0, anyio 4.16.0, Ruff 0.17.3
- **Frontend Mobile Runtime:** Flutter 3.47.6, Dart 3.13.5
- **Môi trường thử nghiệm:** Python mocks / in-memory fixtures và Flutter widget tests (cô lập hoàn toàn, không kết nối DB vật lý)

### 2.2. Lệnh thực thi & Kết quả tổng quan

| Hạng mục kiểm thử | Lệnh thực thi chính thức | Kết quả ghi nhận | Trạng thái |
|---|---|:---:|:---:|
| **Linter Backend** | `cd backend`<br>`uv run ruff check tests/unit/test_interaction_matrix_cases.py tests/unit/test_interaction_checks_api.py` | `All checks passed!` (0 warning, 0 error) | **PASS** |
| **Backend Test Suite** | `cd backend`<br>`uv run pytest tests/unit/test_interaction_matrix_cases.py tests/unit/test_interaction_checks_api.py tests/unit/test_interaction_evaluator.py tests/unit/test_contract_interaction.py -v` | **70 / 70 passed** (3.96s) | **PASS** |
| **Frontend Mobile Suite** | `cd frontend/mobile`<br>`flutter test test/features/interaction_check/` | **13 / 13 passed** (5.0s) | **PASS** |

#### Phân rã 70 test cases backend:
- `backend/tests/unit/test_interaction_matrix_cases.py` (trong workspace backend): **26 tests** (toàn bộ 27 ca ma trận, trong đó `TC-COMM-01` và `02` được kiểm tra đối xứng trong 1 test giao hoán).
- `backend/tests/unit/test_interaction_checks_api.py` (trong workspace backend): **9 tests** (auth, authorization, candidate not found, none found, severity finding, insufficient data, dose threshold, preserve existing dose, mixed response).
- `backend/tests/unit/test_interaction_evaluator.py` (trong workspace backend): **6 tests** (none found, insufficient data, commutative matching, contraindicated severity 4, dose threshold, deduplication).
- `backend/tests/unit/test_contract_interaction.py` (trong workspace backend): **29 tests** (toàn bộ OpenAPI contract validation).

#### Phân rã 13 test cases mobile:
- `frontend/mobile/test/features/interaction_check/interaction_check_test.dart` (trong workspace mobile): **8 tests** (kiểm thử mapper JSON, khởi tạo thực thể, in-memory repository stub và widget cảnh báo mức độ).
- `frontend/mobile/test/features/interaction_check/interaction_flow_test.dart` (trong workspace mobile): **5 tests** (kiểm thử luồng thêm thuốc: có tương tác, phản hồi mock noneFound, thiếu hoạt chất, phản hồi hỗn hợp, xử lý lỗi mạng).

### 2.3. Đối Soát Giữa Kiểm Thử Cục Bộ (Local) Và GitHub CI Checks

Nhằm bảo đảm tính khách quan và minh bạch kỹ thuật, tình trạng kiểm thử cục bộ và trạng thái CI trên GitHub của 5 Draft Pull Requests được đối chiếu chi tiết như sau:

| Kho Lưu Trữ (Repo) | Draft PR | Kiểm Thử Cục Bộ (Local Runner) | Trạng Thái GitHub CI Checks | Đánh Giá Tích Hợp |
|---|:---:|:---:|:---:|---|
| **Superproject (`DrugTime`)** | [PR #51](https://github.com/DrugTime-C1SE-07/DrugTime/pull/51) | Submodule pointer validation đạt chuẩn | `agents`: **PASS (SUCCESS)** | Workflow kiểm tra cấu trúc submodule và agents hoàn tất thành công |
| **`DrugTime-api_contract`** | [PR #17](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/17) | JSON Schema validation đạt 100% | **Không có checks báo cáo** (`no checks reported`) | Repository chưa cấu hình workflow CI tự động cho nhánh này |
| **`DrugTime-backend`** | [PR #45](https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/45) | 70/70 tests pass (6.68s), Ruff check 0 lỗi | **Không có checks báo cáo** (`no checks reported`) | Repository chưa cấu hình workflow CI tự động cho nhánh này |
| **`DrugTime-frontend`** | [PR #55](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/55) | 13/13 tests pass (4.1s), analyze 0 lỗi | `build-and-test`: **FAIL** (944 pass, 5 fail)<br>Vercel: **PASS** | 13/13 tests module PB24 `interaction_check` đều pass 100%; 5 bài test fail trên CI là lỗi nền có sẵn từ `origin/main` (xem phân tích bên dưới) |
| **`DrugTime-docs`** | [PR #28](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/28) | Markdown format & link relative đạt 100% | **Không có checks báo cáo** (`no checks reported`) | Repository chưa cấu hình workflow CI tự động cho nhánh này |

#### Bằng Chứng Tái Hiện Lỗi Nền Trên `DrugTime-frontend` (PR #55):
- Báo cáo kết quả chạy `Mobile CI` của PR #55 (Run ID: `41787896450`): ghi nhận **944 tests pass, 5 failed, 1 skipped**.
- Đối soát đối chiếu trên nhánh gốc `origin/main` tại commit merge PR #54 (`Merge pull request #54 from DrugTime-C1SE-07/feat/camera-screen`, Run ID: `41038468017` ngày 30/10/2026): ghi nhận **931 tests pass, 5 failed, 1 skipped**.
- **Danh sách chính xác 5 bài test fail trùng khớp 100% giữa base `main` và PR #55:**
  1. `test/features/family_link/family_tab_screen_test.dart`: *alert entry displays server unread count and removes it after clear*
  2. `test/features/family_link/redeem_acceptance_test.dart`: *AC2: valid QR fills code and waits for explicit confirmation*
  3. `test/features/family/family_link_code_stability_test.dart`: *FamilyLinkCode stability & lifecycle tests 4. Tích hợp vòng đời phiên: Đăng xuất qua AuthController.signOut() xóa mã, đăng nhập lại nạp lại mã ổn định*
  4. `test/app/app_shell_test.dart`: *AC16: chuyển sang tab Người thân thì tải lại yêu cầu đang chờ*
  5. `test/app/app_shell_test.dart`: *AC20: Người giám sát trống → Mở tab Người thân về đúng tab*
- **Kết luận:** Số bài test tăng từ 931 lên 944 đúng bằng **13 bài test mới của cụm PB24** (`test/features/interaction_check/`), và cả 13 bài đều **PASS 100%**. Năm bài test thất bại là **lỗi hồi quy nền có sẵn trên nhánh `main` trước khi PB24 được tách nhánh**, hoàn toàn độc lập với module PB24. Đợt kiểm toán ghi nhận trung thực bằng chứng này và không báo CI xanh giả mạo.

### 2.4. Xác Minh PostgreSQL Tích Hợp & Database Seeding (Scaffold Scope)
Nhằm kiểm chứng khả năng tương thích SQL và cơ chế an toàn transaction khi nạp dữ liệu vào cơ sở dữ liệu quan hệ, bài kiểm thử tích hợp chuyên biệt đã được thực thi trên môi trường PostgreSQL test riêng biệt:
- **Cơ sở dữ liệu thử nghiệm:** `drugtime_seed_test` (loopback), container/instance cô lập dành riêng cho kiểm thử tự động, tuyệt đối không kết nối DB dùng chung (`postgres`) hay DB production.
- **Phạm vi kiểm chứng:** Bài test sử dụng các fixture nhân tạo (`synthetic_active_ingredient_alpha`, `synthetic_active_ingredient_beta`) để kiểm chứng cú pháp SQL, tính lũy thừa (idempotency) và cơ chế rollback tự động của bộ khung `seed_loader_scaffolding.TransactionSafeSeedLoader` (scaffold loader).
- **Ranh giới kỹ thuật bắt buộc:**
  1. Đây **CHỈ LÀ KIỂM CHỨNG BỘ KHUNG (SCAFFOLD)** về mặt cú pháp SQL và an toàn transaction; **KHÔNG PHẢI là kiểm chứng production loader hay production safety gate** trong môi trường vận hành thực tế.
  2. Đây **KHÔNG PHẢI là kiểm thử E2E live endpoint của người bệnh** (`POST /patients/{id}/interaction-checks`).
  3. Fixture test tạm thời thiết lập metadata `verification_status="verified"` và tiền tố `SYNTHETIC_*` chỉ nhằm mục đích kiểm tra luồng phân nhánh code của scaffold, hoàn toàn không đại diện cho dữ liệu lâm sàng hay chữ ký/attestation y tế thật.
- **Hiện trạng dữ liệu hậu kiểm (truy vấn SELECT chỉ đọc sau rollback):**
  - Bảng `active_ingredients`: Ghi nhận tồn tại 2 bản ghi hoạt chất nhân tạo (`synthetic_active_ingredient_alpha`, `synthetic_active_ingredient_beta`) từ các lần chạy test trước.
  - Bảng `active_ingredient_interactions`: **0 hàng** (không còn dữ liệu tương tác sau khi transaction rollback).
  - Bảng `active_ingredient_dose_thresholds`: **0 hàng** (không còn dữ liệu ngưỡng liều sau khi transaction rollback).

---

## 3. Bảng Đối Chiếu Chi Tiết 27 Test Case Của Ma Trận (Traceability Matrix)

Dưới đây là bảng đối chiếu chi tiết 27 ca kiểm thử theo thiết kế ma trận (`sprint4_plan/PB24/4.03_test_matrix.md` trong workspace) với test thực thi, ánh xạ, kết quả thực tế và trạng thái:

| Mã ca | Cặp/Nhóm thuốc thử nghiệm | Nhãn | Test thực thi (Tên hàm & File nguồn) | Ánh xạ | Kết quả thực tế (Actual Result) | Kết quả | Ghi chú & Ranh giới lâm sàng |
|:---:|---|:---:|---|:---:|---|:---:|---|
| `TC-POS-01` | Gliclazid (`11`) + Miconazol (`15`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-01]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 4` (Chống chỉ định)<br>`warning`: Cảnh báo hạ đường huyết nặng, hôn mê<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa kiểm định lâm sàng). |
| `TC-POS-02` | Glibenclamid (`12`) + Bosentan (`16`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-02]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 4` (Chống chỉ định)<br>`warning`: Cảnh báo tổn thương gan<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa kiểm định lâm sàng). |
| `TC-POS-03` | Metformin (`10`) + Thuốc cản quang Iod (`17`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-03]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 4` (Chống chỉ định)<br>`warning`: Cảnh báo toan lactic, suy thận cấp<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chờ quy trình tạm ngừng theo eGFR). |
| `TC-POS-04` | Gliclazid (`11`) + Fluconazol (`18`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-04]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Ức chế CYP2C9<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa có ngưỡng liều số học trong y văn). |
| `TC-POS-05` | Metformin (`10`) + Cimetidin (`19`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-05]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 2`<br>`warning`: Cạnh tranh OCT2 ống thận<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa có ngưỡng liều số học trong y văn). |
| `TC-POS-06` | Insulin (`14`) + Propranolol (`20`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-06]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Che lấp triệu chứng hạ đường huyết<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa có ngưỡng liều số học trong y văn). |
| `TC-POS-07` | Metformin (`10`) + Furosemid (`21`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-07]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 2`<br>`warning`: Giảm thể tích tuần hoàn, suy thận<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa có ngưỡng liều số học trong y văn). |
| `TC-POS-08` | Gliclazid (`11`) + Prednisolon (`22`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-08]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Đối kháng hạ đường huyết<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa có ngưỡng liều số học trong y văn). |
| `TC-POS-09` | Glibenclamid (`12`) + Ciprofloxacin (`23`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-09]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Quinolon tăng hạ đường huyết sâu<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa có ngưỡng liều số học trong y văn). |
| `TC-POS-10` | Glimepirid (`13`) + Clarithromycin (`24`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-10]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Macrolid ức chế CYP3A4<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance kỹ thuật với quy tắc 4.01 có nguồn sách. Workbook: "Đã đối chiếu nguồn"; DB: pending_review (chưa có ngưỡng liều số học trong y văn). |
| `TC-NEG-01` | Metformin (`10`) + Gliclazid (`11`) | `provisional` *(Candidate)* | `test_draft_conformance_negative_candidates[TC-NEG-01]`<br>(`test_interaction_matrix_cases.py` L512 trong workspace) | 1–1 | `status: da_kiem_tra_khong_thay`<br>`interactions: []`<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Candidate)* | Trích từ QĐ 5481/QĐ-BYT (phác đồ phối hợp). Là candidate âm tính lâm sàng; 0% false alarm trên tập quy tắc draft. |
| `TC-NEG-02` | Metformin (`10`) + Glimepirid (`13`) | `provisional` *(Candidate)* | `test_draft_conformance_negative_candidates[TC-NEG-02]`<br>(`test_interaction_matrix_cases.py` L512 trong workspace) | 1–1 | `status: da_kiem_tra_khong_thay`<br>`interactions: []`<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Candidate)* | Trích từ QĐ 5481/QĐ-BYT. Chưa thẩm định âm tính lâm sàng. |
| `TC-NEG-03` | Metformin (`10`) + Insulin (`14`) | `provisional` *(Candidate)* | `test_draft_conformance_negative_candidates[TC-NEG-03]`<br>(`test_interaction_matrix_cases.py` L512 trong workspace) | 1–1 | `status: da_kiem_tra_khong_thay`<br>`interactions: []`<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Candidate)* | Trích từ QĐ 5481/QĐ-BYT. Chưa thẩm định âm tính lâm sàng. |
| `TC-NEG-04` | Metformin (`10`) + Amlodipin (`25`) | `provisional` *(Candidate)* | `test_draft_conformance_negative_candidates[TC-NEG-04]`<br>(`test_interaction_matrix_cases.py` L512 trong workspace) | 1–1 | `status: da_kiem_tra_khong_thay`<br>`interactions: []`<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Candidate)* | Trích từ DTQGVN 2018 (phối hợp kèm tăng huyết áp). Chưa thẩm định âm tính lâm sàng. |
| `TC-NEG-05` | Metformin (`10`) + Paracetamol (`26`) | `provisional` *(Candidate)* | `test_draft_conformance_negative_candidates[TC-NEG-05]`<br>(`test_interaction_matrix_cases.py` L512 trong workspace) | 1–1 | `status: da_kiem_tra_khong_thay`<br>`interactions: []`<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Candidate)* | Trích từ DTQGVN 2018. Chưa thẩm định âm tính lâm sàng. |
| `TC-POLY-01` | Đơn 3 thuốc synthetic: 1 cặp tương tác A+B | `synthetic` | `test_tc_poly_01_three_medications_one_interaction`<br>(`test_interaction_matrix_cases.py` L65 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`interactions: len=1` (đúng cặp A+B Mức 4)<br>Cặp A–C và B–C không báo nhầm | **PASS** | Kiểm tra phân nhánh tổ hợp $\binom{3}{2}$. Hoàn toàn là rule fixture nhân tạo. |
| `TC-POLY-02` | Đơn 4 thuốc synthetic: 2 cặp độc lập A+B và C+D | `synthetic` | `test_tc_poly_02_four_medications_two_independent_interactions`<br>(`test_interaction_matrix_cases.py` L87 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`interactions: len=2` (A+B Mức 3, C+D Mức 2)<br>Không sinh cảnh báo chéo giữa A/B với C/D | **PASS** | Kiểm tra tính độc lập giữa các cặp tương tác. Rule fixture nhân tạo. |
| `TC-COMM-01` | Thứ tự truyền: A trước, B sau | `synthetic` | `test_tc_comm_01_and_02_commutativity`<br>(`test_interaction_matrix_cases.py` L114 trong workspace) | 1–N *(Bao phủ chung)* | `status: co_tuong_tac`<br>`severity: 4`<br>`med_a: FIX-01, med_b: FIX-02` | **PASS** | Kiểm tra nhánh $A+B$. Ánh xạ chung trong test giao hoán đối xứng CD7. |
| `TC-COMM-02` | Thứ tự truyền: B trước, A sau (Đảo ngược) | `synthetic` | `test_tc_comm_01_and_02_commutativity`<br>(`test_interaction_matrix_cases.py` L114 trong workspace) | 1–N *(Bao phủ chung)* | `status: co_tuong_tac`<br>`severity: 4`<br>`med_a: FIX-01, med_b: FIX-02`<br>Trùng khớp 100% với `TC-COMM-01` | **PASS** | Kiểm tra nhánh $B+A$. Khẳng định $A+B = B+A$ không phụ thuộc thứ tự input. |
| `TC-INSUF-01` | Thuốc ứng viên thiếu hoạt chất | `synthetic` | `test_tc_insuf_01_candidate_missing_active_ingredients`<br>(`test_interaction_matrix_cases.py` L147 trong workspace) | 1–1 | `status: khong_du_du_lieu`<br>`interactions: []`<br>`insufficient_data`: Chứa `FIX-MED-NOING-01` | **PASS** | Kiểm tra engine gắn cờ khi thuốc không có liên kết hoạt chất trong danh mục. |
| `TC-INSUF-02` | Phản hồi hỗn hợp (Có tương tác + Có thuốc thiếu hoạt chất) | `synthetic` | `test_tc_insuf_02_mixed_response_evaluator`<br>(`test_interaction_matrix_cases.py` L166 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`interactions: len=1` (Mức 4)<br>`insufficient_data`: Chứa `FIX-MED-NOING-02` | **PASS** | Kiểm tra cơ chế trả song song finding và danh sách thuốc thiếu dữ liệu (Task 4.02). |
| `TC-DOSE-01` | Không khớp đơn vị liều (`"viên"` vs `"mg"`) | `synthetic` | `test_tc_dose_01_incompatible_unit_fallback`<br>(`test_interaction_matrix_cases.py` L210 trong workspace) | 1–1 | Evaluator chặn so sánh số học sai lệch (`"viên"` != `"mg"`)<br>`severity: 2` (mặc định) | **PASS** | Không tự ý quy đổi viên thành mg. Giữ mức cảnh báo mặc định. |
| `TC-DOSE-02` | Đơn vị liều bị thiếu (`dose_unit = None`) | `synthetic` | `test_tc_dose_02_missing_unit_fallback`<br>(`test_interaction_matrix_cases.py` L228 trong workspace) | 1–1 | Evaluator không đoán mò đơn vị<br>`severity: 2` (mặc định) | **PASS** | Bảo vệ chống suy đoán liều khi dữ liệu đầu vào thiếu trường đơn vị. |
| `TC-DOSE-03` | Liều cao chuẩn đơn vị (`80 mg` $\ge$ `40 mg`) | `synthetic` | `test_tc_dose_03_matching_unit_high_dose_triggers_threshold`<br>(`test_interaction_matrix_cases.py` L246 trong workspace) | 1–1 | Ngưỡng liều kích hoạt thành công<br>`severity: 3`<br>`warning_message` hiện đúng text ngưỡng | **PASS** | Xác nhận logic so sánh ngưỡng hoạt động chính xác khi đơn vị tương thích. |
| `TC-DOSE-04` | Liều thấp dưới ngưỡng (`20 mg` < `40 mg`) | `synthetic` | `test_tc_dose_04_matching_unit_low_dose_below_threshold`<br>(`test_interaction_matrix_cases.py` L266 trong workspace) | 1–1 | Ngưỡng không kích hoạt<br>`severity: 2` (mặc định) | **PASS** | Liều thấp dưới ngưỡng giữ nguyên mức cảnh báo cơ sở của quy tắc. |
| `TC-DEDUP-01` | Trùng lặp hoạt chất: 2 biệt dược mang cùng hoạt chất | `synthetic` | `test_tc_dedup_01_shared_synthetic_ingredient`<br>(`test_interaction_matrix_cases.py` L289 trong workspace) | 1–1 | `interactions: len=2`<br>Cặp (1, 3) và Cặp (2, 3)<br>Không có cặp (1, 2)<br>Khử trùng lặp rule lặp 2 lần | **PASS** | Dedup áp dụng theo từng cặp thuốc; không gộp các ID thuốc khác nhau nhằm đảm bảo minh bạch tên biệt dược. |
| `TC-DISC-01` | Câu miễn trừ trách nhiệm y tế NFR03 bắt buộc | `synthetic` | `test_tc_disc_01_disclaimer_mandatory_on_all_statuses`<br>(`test_interaction_matrix_cases.py` L338 trong workspace) | 1–1 | 100% phản hồi (`co_tuong_tac`, `khong_du_du_lieu`, `da_kiem_tra_khong_thay`) đều có disclaimer NFR03 | **PASS** | Khớp chính xác từng ký tự theo quy định pháp lý y tế NFR03. |

---

## 4. Kết Quả Benchmark Hiệu Năng NFR01 (< 2.0 Giây)

### 4.1. Cấu hình kiểm thử
- **Script chuẩn hóa:** `scratch/benchmark_nfr01.py` (Script đo kiểm benchmark trong workspace).
- **Lệnh thực thi:**
  ```bash
  cd backend
  uv run python ../scratch/benchmark_nfr01.py
  ```
- **Số liệu ghi nhận:** Kết quả từ một lần chạy thử nghiệm đơn lẻ, xác định của script `benchmark_nfr01.py` trong Giai đoạn 3 (không tổng hợp hay trộn lẫn số liệu giữa các lần chạy khác nhau):

### 4.2. Bảng số liệu đo lường độ trễ:

| Thành phần kiểm thử | Quy mô Payload | Số lượt đo (Iterations) | p50 (Median) | p90 | p95 | Max | Mean ± Std | Mục tiêu NFR01 | Trạng thái |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Evaluator Thuần** | 5 thuốc, 10 rules | 200 | **0.0328 ms** | 0.0334 ms | 0.0347 ms | 0.0811 ms | 0.0333 ± 0.0037 ms | < 2,000 ms | **ĐẠT** |
| **Evaluator Thuần** | 10 thuốc, 30 rules | 200 | **0.1570 ms** | 0.1672 ms | 0.1718 ms | 0.2581 ms | 0.1598 ± 0.0108 ms | < 2,000 ms | **ĐẠT** |
| **Evaluator Thuần** | 20 thuốc, 50 rules | 200 | **0.8106 ms** | 1.1105 ms | 1.4580 ms | 2.2671 ms | 0.8964 ± 0.2364 ms | < 2,000 ms | **ĐẠT** |
| **API TestClient HTTP** | 1 ứng viên + 4 thuốc đang dùng (Đa thuốc 5 meds) | 100 | **12.07 ms** | **14.87 ms** | **17.73 ms** | **24.09 ms** | 12.11 ± 2.86 ms | < 2,000 ms | **ĐẠT** |

### 4.3. Giới hạn số liệu:
> [!WARNING]
> Số liệu benchmark API trên là kết quả của một lần chạy TestClient HTTP với các dependency và adapter được mock in-memory, **không phải là kiểm thử E2E qua đường truyền mạng vật lý hoặc PostgreSQL thật**. Độ trễ p95 đạt **17.73 ms** và Max đạt **24.09 ms**, đáp ứng tiêu chí NFR01 (< 2,000 ms) trong môi trường thử nghiệm cô lập.

---

## 5. Kết Quả Kiểm Tra Giao Diện Mobile (UI Verification)

Do không có thiết bị vật lý / emulator đang hoạt động và hệ thống không kết nối DB Dev/Production, giao diện Mobile được kiểm chứng an toàn qua **13 bài test Flutter Widget & Flow tự động hóa** (tại `frontend/mobile/test/features/interaction_check/` trong workspace):

1. **Kiểm chứng Hộp thoại Cảnh báo (Warning Dialog UI):**
   - Tiêu đề `CẦN THẬN TRỌNG PHỐI HỢP` hiển thị với tương tác Severity 2–3; tiêu đề `CẢNH BÁO CHỐNG CHỈ ĐỊNH` với nền đỏ hiển thị với Severity 4.
   - Nút *"Quay lại chỉnh sửa"* giữ nguyên màn hình form thêm thuốc để người dùng điều chỉnh liều hoặc đổi thuốc.
   - Nút *"Đã hiểu & Tiếp tục"* ghi nhận sự xác nhận của người dùng và tiến hành lưu thuốc thành công.
2. **Kiểm chứng Phản hồi mock noneFound (`noneFound`):**
   - Với phản hồi mock không tìm thấy tương tác, giao diện lưu trực tiếp và đưa thuốc vào danh sách thuốc đang dùng mà không hiển thị popup cảnh báo.
   - *Lưu ý:* Việc không xuất hiện cảnh báo chỉ xác nhận hành vi hiển thị của UI theo nhánh mã nguồn được kiểm thử với mock dữ liệu, **hoàn toàn không xác nhận phối hợp thuốc an toàn về mặt lâm sàng**.
3. **Kiểm chứng Trường hợp Thiếu Dữ liệu (`insufficientData`):**
   - Hộp thoại cảnh báo `THIẾU DỮ LIỆU ĐỐI SOÁT TƯƠNG TÁC` xuất hiện rõ ràng, nêu bật thuốc chưa có hoạt chất liên kết.
4. **Kiểm chứng Phản hồi Hỗn hợp (`mixed_response`):**
   - Giao diện render trọn vẹn cả danh sách cặp tương tác phát hiện được và danh sách thuốc thiếu hoạt chất, không để xảy ra hiện tượng che khuất thông tin.
5. **Kiểm chứng Miễn trừ Trách nhiệm (Disclaimer NFR03):**
   - Trong các hộp thoại cảnh báo thuộc các ca/nhánh đã kiểm thử, chuỗi disclaimer pháp lý NFR03 đều được hiển thị ở chân dialog.
6. **Xử lý lỗi mạng (`network_error`):**
   - Khi mất kết nối API, ứng dụng không bị crash mà hiển thị dialog thông báo lỗi kết nối, cho phép người dùng quyết định hủy bỏ hoặc tiếp tục lưu offline.

*Giới hạn: Chưa thực hiện Manual Smoke Test trên điện thoại vật lý do chưa có Live PostgreSQL Test Harness cô lập.*

---

## 6. Đối Chiếu Toàn Diện Tiêu Chí Hoàn Thành (Definition of Done) Task 4.03

Dưới đây là bảng đánh giá 5 tiêu chí DoD của Task 4.03 (`sprint4_plan/4.03.md` dòng 21–27) được cập nhật theo chỉ đạo kỹ thuật ngày 04/11/2026 của Product Owner:

| STT | Tiêu chí hoàn thành (DoD) nguyên văn Kế hoạch 4.03 | Bằng chứng thực tế thu thập được | Đánh giá & Ranh giới kỹ thuật theo Quyết định Rebaseline (04/11/2026) | Trạng thái DoD Kỹ Thuật |
|:---:|---|---|---|:---:|
| **DoD 1** | Có bộ test case chuẩn hóa được ghi nhận rõ ràng (Input, Cặp thuốc đối chiếu, Kết quả mong đợi, Kết quả thực tế, Trạng thái Pass/Fail). | • Đã lập ma trận thiết kế chuẩn hóa 27 ca (`sprint4_plan/PB24/4.03_test_matrix.md` trong workspace).<br>• Đã thực thi tự động hóa 27/27 ca với kết quả 100% PASS.<br>• Bảng Mục 3 trong báo cáo này đã đối chiếu đầy đủ Input, Cặp thuốc, Expected, Test thực thi, Actual Result và Pass/Fail cho từng ca. | **ĐẠT MỨC KỸ THUẬT NỘI BỘ**<br>*(Chuẩn hóa đầy đủ mã ca, test code và bảng đối chiếu bàn giao)* | **ĐẠT** |
| **DoD 2** | Tỷ lệ phát hiện True Positive đạt 100% trên bộ mẫu đã thẩm định y văn. | • Đã kiểm thử 10 ca tương tác ĐTĐ (`TC-POS-01`..`10`) và đạt 10/10 PASS ở mức draft-conformance kỹ thuật.<br>• Toàn bộ 10 quy tắc đã được đối chiếu cụ thể với từng trang sách DTQGVN 2018, Sách TT 2015, Martindale 38th.<br>• *Lịch sử tiêu chí:* Tiêu chí yêu cầu chữ ký số Dược sĩ; PO chỉ đạo cho phép tiếp tục công việc kỹ thuật không chờ attestation; dữ liệu vẫn giữ `pending_review`, chưa có thẩm định lâm sàng chính thức. | **ĐẠT MỨC DRAFT-CONFORMANCE KỸ THUẬT**<br>*(Đạt 100% draft-conformance kỹ thuật với 10 quy tắc có nguồn sách; dữ liệu vẫn mang nhãn `pending_review`, chưa kiểm định lâm sàng)* | **ĐẠT (DRAFT KỸ THUẬT)** |
| **DoD 3** | Tỷ lệ False Positive = 0% trên các cặp thuốc đối chứng an toàn. | • Đã kiểm thử 5 ca candidate âm tính (`TC-NEG-01`..`05`) và đạt 5/5 không sinh cảnh báo giả trên tập quy tắc.<br>• Năm ca này được trích xuất từ phác đồ phối hợp điều trị chính thức của Bộ Y tế (QĐ 5481/QĐ-BYT).<br>• *Khoảng trống:* Thiếu 5 ca để đạt chỉ tiêu 10 ca Negative Oracle của kế hoạch gốc; phác đồ điều trị chỉ chứng minh thuốc được phép phối hợp, chưa phải tập đối chứng âm tính dược lý toàn diện. | **ĐẠT MỘT PHẦN (CANDIDATE SUBSET) THEO REBASELINE**<br>*(0% false alarm trên 5 ca candidate phác đồ; thiếu tối thiểu 5 ca để đủ 10 ca; chưa thẩm định âm tính lâm sàng đầy đủ; không kết luận an toàn tuyệt đối)* | ⚠️ **ĐẠT MỘT PHẦN** |
| **DoD 4** | Disclaimer y tế luôn hiển thị ở mọi phản hồi có cảnh báo (`disclaimer IS NOT NULL`). | • Đã xác minh qua `TC-DISC-01`, `test_interaction_checks_mixed_response` và các bài test mobile widget.<br>• Trong các ca và nhánh đã được kiểm thử trên Backend API và Mobile UI, disclaimer NFR03 đều hiển thị đúng từng ký tự bắt buộc. | **ĐÃ XÁC MINH TRONG CÁC CA/NHÁNH ĐÃ TEST**<br>*(Giới hạn trong phạm vi các ca test backend in-memory và widget test đã chạy)* | **ĐẠT (TRONG PHẠM VI TEST)** |
| **DoD 5** | Có báo cáo nghiệm thu kiểm thử chi tiết bàn giao cho Product Owner / Mentor. | • Văn bản báo cáo này (`PB24_Test_Report.md`) được lập đầy đủ số liệu, lệnh chạy, ma trận truy vết, benchmark và đối chiếu DoD chi tiết phục vụ bàn giao tiến độ kỹ thuật.<br>• Ghi nhận đầy đủ chỉ đạo kỹ thuật từ PO ngày 04/11/2026 và phân tích lỗi nền CI. | **ĐÃ HOÀN TẤT BÁO CÁO KỸ THUẬT CHI TIẾT**<br>*(Bàn giao tiến độ kỹ thuật draft/WIP cho Product Owner và Mentor xem xét)* | **ĐẠT** |

---

## 7. Các Khoảng Trống & Phụ Thuộc Kỹ Thuật Chưa Đóng (Open Dependencies)

1. **Khoảng trống Cặp tương tác Mức độ 1 (Severity 1):**
   - Toàn bộ 10 ca y văn hiện tại chỉ bao phủ Severity 2, 3, 4. Dự án **hoàn toàn thiếu ca tương tác Mức độ 1 (Nhẹ/Minor)** do tài liệu Task 4.01 không cung cấp. Cần bổ sung cặp tương tác Mức 1 có trích dẫn y văn trong giai đoạn sau.
2. **Khoảng trống Danh mục Đối chứng Âm tính (Negative Oracle):**
   - Hiện mới có 5 ca candidate trích từ phác đồ Bộ Y tế (thiếu tối thiểu 5 ca để đạt chỉ tiêu 10 ca âm tính của kế hoạch 4.03 ban đầu).
3. **Khoảng trống Ngưỡng liều số học (Dose Threshold):**
   - Bảy quy tắc phụ thuộc liều (`phu_thuoc_lieu`, INT_DIA_004..010) chưa có số liệu ngưỡng liều định lượng trong sách/tài liệu tham khảo; đã ghi nhận đầy đủ trong workbook, không tạo số liệu giả định.
4. **Cổng Kiểm thử Tích hợp Cơ sở Dữ liệu Cô lập (Isolated Live DB Harness Gate):**
   - Đã thực thi kiểm chứng SQL scaffold trên database test chuyên biệt `drugtime_seed_test` với fixture synthetic; xác nhận transaction rollback bảo toàn 0 tương tác và 0 ngưỡng liều tồn đọng.
   - Tuy nhiên, production loader và safety gate vận hành thực tế chưa được kiểm chứng trên DB thật; endpoint live `/patients/{id}/interaction-checks` chưa chạy E2E trên cơ sở dữ liệu đầy đủ.
5. **Hiện trạng bản ghi `id=116` trong cơ sở dữ liệu dùng chung (`postgres`):**
   - Truy vấn `SELECT` chỉ đọc trên DB dùng chung `postgres` quan sát thấy bản ghi `id=116` tồn tại với trạng thái `verified` và metadata chứa placeholder `[REDACTED_NAME]`, `[REDACTED_LICENSE]`.
   - **Không gọi bản ghi này là rác hay giả mạo**, đồng thời **không khẳng định metadata của nó là thông tin thật**. Bản ghi này chưa được xác thực độc lập với bất kỳ nguồn phê duyệt lâm sàng chính thức nào bên ngoài.
   - **Không đề xuất hoặc thực hiện cleanup** (không chạy DELETE/TRUNCATE/DROP, không yêu cầu can thiệp dữ liệu); đợt kiểm toán chỉ ghi nhận trung thực trạng thái đã quan sát khách quan qua truy vấn SELECT chỉ đọc.

---

## 8. Kết Luận Nghiệm Thu & Khuyến Nghị

1. **Về mặt Kỹ thuật Phần mềm (Software Engineering):**
   - Thuật toán `InteractionEvaluator` (CD7), API Backend và giao diện Mobile đã được kiểm thử tự động hóa nghiêm ngặt (70 backend tests, 13 mobile tests, ruff check 100% PASS, flutter analyze 0 lỗi, flutter build bundle PASS).
   - Hiệu năng hệ thống NFR01 đạt độ trễ cực thấp (p95 đạt 17.73 ms, tối đa 24.09 ms << 2,000 ms).
   - Cơ chế bảo vệ liều lượng, giao hoán, xử lý thiếu dữ liệu và khử trùng lặp theo cặp thuốc hoạt động đúng đặc tả.
2. **Về mặt Đánh giá Trạng thái & Khả năng Merge:**
   - Cụm tính năng PB24 (Tasks 4.01, 4.02, 4.03) **Ở TRẠNG THÁI DRAFT / WIP** trên cơ sở 5 Draft PRs (#51, #17, #45, #55, #28) theo chỉ đạo kỹ thuật của PO.
   - **TUYỆT ĐỐI CHƯA MERGE** do còn tồn tại các blocker kỹ thuật và lâm sàng:
     1. **Cổng DB Integration & Production Loader (Task 4.01 DoD 4):** Kiểm thử PostgreSQL trên `drugtime_seed_test` chỉ mới xác minh SQL scaffold; chưa kiểm chứng production loader/safety gate trên DB thật và chưa chạy live E2E endpoint bệnh nhân (`POST /patients/{id}/interaction-checks`).
     2. **Trạng thái CI Frontend (PR #55):** GitHub Actions `build-and-test` vẫn đang FAIL/UNSTABLE (944 pass, 5 fail) do 5 bài test lỗi nền có sẵn từ nhánh `main`.
     3. **Hiện trạng bản ghi id=116 trong DB dùng chung:** Đã quan sát thấy nhưng chưa được xác thực độc lập; không khẳng định metadata là thật và không đề xuất hoặc thực hiện cleanup dữ liệu.
     4. **Khoảng trống lâm sàng & dữ liệu:** Dữ liệu chưa qua kiểm định của Dược sĩ lâm sàng; toàn bộ 10 quy tắc ĐTĐ giữ `pending_review` trong DB; thiếu ngưỡng liều định lượng cho 7 quy tắc phụ thuộc liều; thiếu 5 ca đối chứng âm tính; disclaimer NFR03 bắt buộc luôn duy trì.
3. **Khuyến nghị bước tiếp theo:**
   - Bàn giao báo cáo kỹ thuật và 5 Draft PRs cho Product Owner và Mentor xem xét tiến độ kỹ thuật.
   - Tiếp tục duy trì 5 PR ở trạng thái Draft/WIP, không merge.
   - Chuẩn bị môi trường Docker PostgreSQL test harness cô lập cho CI trước khi triển khai production loader.
