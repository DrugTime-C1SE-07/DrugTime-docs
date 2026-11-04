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
> - **Chưa thực hiện Live DB E2E:** Dự án chưa thiết lập môi trường test harness PostgreSQL cô lập riêng biệt. Do đó, các bài test API được thực hiện qua FastAPI `TestClient` với mock adapters; không đánh đồng với kiểm thử tích hợp Live DB thật.
> - **Chưa kiểm thử trên thiết bị di động vật lý:** Toàn bộ 13 bài test Flutter được thực hiện trên headless widget/flow test runner, chưa chạy trên thiết bị iOS/Android vật lý.
> - **Phân tách rạch ròi giữa Lâm sàng và Kỹ thuật:**
>   - 10 ca tương tác ĐTĐ (`TC-POS-01`..`10`) và 5 ca candidate âm tính (`TC-NEG-01`..`05`) được gắn nhãn `provisional`. Toàn bộ dữ liệu lâm sàng giữ nguyên trạng thái `pending_review` (chưa có chữ ký Dược sĩ lâm sàng); kết quả test chỉ chứng minh **draft-conformance kỹ thuật** với tập quy tắc dự thảo, **không tuyên bố độ chính xác y khoa (True Positive/False Positive lâm sàng)**.
>   - 17 hoạt chất OTC (vai trò `trieu_chung_cap_tinh`) đã được chuyển sang thư mục `markdown/OTC_Phase2/` và loại khỏi deliverable PB24 đợt này, bảo lưu hồ sơ chứng cứ cho Phase 2.
>   - 12 ca kỹ thuật (`synthetic`) sử dụng 100% định danh nhân tạo thuần túy để kiểm chứng cơ chế logic phần mềm, không đại diện cho tương tác lâm sàng.

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
| **Superproject (`DrugTime`)** | [PR #51](https://github.com/DrugTime-C1SE-07/DrugTime/pull/51) | Submodule pointer validation đạt chuẩn | `agents`: **PASS (7s)** | Workflow kiểm tra cấu trúc submodule và agents hoàn tất thành công |
| **`DrugTime-api_contract`** | [PR #17](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/17) | JSON Schema validation đạt 100% | **Không có checks báo cáo** (`no checks reported`) | Repository chưa cấu hình workflow CI tự động cho nhánh này |
| **`DrugTime-backend`** | [PR #45](https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/45) | 70/70 tests pass (6.68s), Ruff check 0 lỗi | **Không có checks báo cáo** (`no checks reported`) | Repository chưa cấu hình workflow CI tự động cho nhánh này |
| **`DrugTime-frontend`** | [PR #55](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/55) | 13/13 tests pass (4.1s), analyze 0 lỗi | `build-and-test`: **FAIL**<br>Vercel: **PASS** | 13/13 tests module PB24 `interaction_check` đều pass; 5 bài test fail trên CI thuộc về module `family_link` và `app_shell` có sẵn từ trước trên `main` |
| **`DrugTime-docs`** | [PR #28](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/28) | Markdown format & link relative đạt 100% | **Không có checks báo cáo** (`no checks reported`) | Repository chưa cấu hình workflow CI tự động cho nhánh này |

---

## 3. Bảng Đối Chiếu Chi Tiết 27 Test Case Của Ma Trận (Traceability Matrix)

Dưới đây là bảng đối chiếu chi tiết 27 ca kiểm thử theo thiết kế ma trận (`sprint4_plan/PB24/4.03_test_matrix.md` trong workspace) với test thực thi, ánh xạ, kết quả thực tế và trạng thái:

| Mã ca | Cặp/Nhóm thuốc thử nghiệm | Nhãn | Test thực thi (Tên hàm & File nguồn) | Ánh xạ | Kết quả thực tế (Actual Result) | Kết quả | Ghi chú & Ranh giới lâm sàng |
|:---:|---|:---:|---|:---:|---|:---:|---|
| `TC-POS-01` | Gliclazid (`11`) + Miconazol (`15`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-01]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 4` (Chống chỉ định)<br>`warning`: Cảnh báo hạ đường huyết nặng, hôn mê<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review` (chưa có chữ ký Dược sĩ, chưa tính True Positive lâm sàng). |
| `TC-POS-02` | Glibenclamid (`12`) + Bosentan (`16`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-02]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 4` (Chống chỉ định)<br>`warning`: Cảnh báo tổn thương gan<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review`. |
| `TC-POS-03` | Metformin (`10`) + Thuốc cản quang Iod (`17`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-03]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 4` (Chống chỉ định)<br>`warning`: Cảnh báo toan lactic, suy thận cấp<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review` (chờ quy trình tạm ngừng theo eGFR). |
| `TC-POS-04` | Gliclazid (`11`) + Fluconazol (`18`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-04]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Ức chế CYP2C9<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review`. |
| `TC-POS-05` | Metformin (`10`) + Cimetidin (`19`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-05]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 2`<br>`warning`: Cạnh tranh OCT2 ống thận<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review`. |
| `TC-POS-06` | Insulin (`14`) + Propranolol (`20`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-06]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Che lấp triệu chứng hạ đường huyết<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review`. |
| `TC-POS-07` | Metformin (`10`) + Furosemid (`21`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-07]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 2`<br>`warning`: Giảm thể tích tuần hoàn, suy thận<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review`. |
| `TC-POS-08` | Gliclazid (`11`) + Prednisolon (`22`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-08]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Đối kháng hạ đường huyết<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review`. |
| `TC-POS-09` | Glibenclamid (`12`) + Ciprofloxacin (`23`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-09]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Quinolon tăng hạ đường huyết sâu<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review`. |
| `TC-POS-10` | Glimepirid (`13`) + Clarithromycin (`24`) | `provisional` | `test_draft_conformance_positive_cases[TC-POS-10]`<br>(`test_interaction_matrix_cases.py` L468 trong workspace) | 1–1 | `status: co_tuong_tac`<br>`severity: 3`<br>`warning`: Macrolid ức chế CYP3A4<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Draft)* | Đạt Conformance với quy tắc nháp 4.01. Đang `pending_review`. |
| `TC-NEG-01` | Metformin (`10`) + Gliclazid (`11`) | `provisional` *(Candidate)* | `test_draft_conformance_negative_candidates[TC-NEG-01]`<br>(`test_interaction_matrix_cases.py` L512 trong workspace) | 1–1 | `status: da_kiem_tra_khong_thay`<br>`interactions: []`<br>`disclaimer`: NFR03 đầy đủ | **PASS** *(Candidate)* | Trích từ QĐ 5481/QĐ-BYT (phác đồ phối hợp). Chưa có attestation Dược sĩ, KHÔNG tính True Negative. |
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

Dưới đây là bảng đánh giá nghiêm ngặt 5 tiêu chí DoD nguyên văn của Task 4.03 (`sprint4_plan/4.03.md` dòng 21–27):

| STT | Tiêu chí hoàn thành (DoD) nguyên văn Kế hoạch 4.03 | Bằng chứng thực tế thu thập được | Đánh giá & Ranh giới kỹ thuật | Trạng thái DoD |
|:---:|---|---|---|:---:|
| **DoD 1** | Có bộ test case chuẩn hóa được ghi nhận rõ ràng (Input, Cặp thuốc đối chiếu, Kết quả mong đợi, Kết quả thực tế, Trạng thái Pass/Fail). | • Đã lập ma trận thiết kế chuẩn hóa 27 ca (`sprint4_plan/PB24/4.03_test_matrix.md` trong workspace).<br>• Đã thực thi tự động hóa 27/27 ca với kết quả 100% PASS.<br>• Bảng Mục 3 trong báo cáo này đã đối chiếu đầy đủ Input, Cặp thuốc, Expected, Test thực thi, Actual Result và Pass/Fail cho từng ca. | **ĐẠT MỨC KỸ THUẬT NỘI BỘ**<br>*(Đã chuẩn hóa đầy đủ mã ca, test code và bảng đối chiếu bàn giao)* | **ĐẠT** |
| **DoD 2** | Tỷ lệ phát hiện True Positive đạt 100% trên bộ mẫu đã thẩm định y văn. | • Đã kiểm thử 10 ca tương tác ĐTĐ (`TC-POS-01`..`10`) và đạt 10/10 PASS ở mức draft-conformance kỹ thuật.<br>• Tuy nhiên, **toàn bộ 10 ca này vẫn đang `pending_review` từ Task 4.01**, chưa có chữ ký số/attestation từ Dược sĩ lâm sàng có thẩm quyền. | **CHƯA ĐƯỢC CHỨNG MINH / CHƯA ĐÁNH GIÁ ĐƯỢC**<br>*(Số ca verified y văn chính thức = 0; chưa có bộ mẫu đã thẩm định để đo lường tỷ lệ True Positive lâm sàng; không coi đây là test thất bại)* | **CHƯA ĐÁNH GIÁ ĐƯỢC**<br>*(Chờ clinical sign-off 4.01)* |
| **DoD 3** | Tỷ lệ False Positive = 0% trên các cặp thuốc đối chứng an toàn. | • Đã kiểm thử 5 ca candidate âm tính (`TC-NEG-01`..`05`) và đạt 5/5 không sinh cảnh báo giả trên tập quy tắc nháp.<br>• Tuy nhiên, **5 ca này mới trích từ phác đồ điều trị của Bộ Y tế**, chưa được Dược sĩ lâm sàng thẩm định và phê duyệt thành danh mục True-Negative Oracle chính thức. | **CHƯA ĐƯỢC CHỨNG MINH / CHƯA ĐÁNH GIÁ ĐƯỢC**<br>*(Chưa có danh mục True-Negative Oracle được duyệt; chưa có cơ sở xác lập mẫu số và tử số; không coi đây là test thất bại)* | **CHƯA ĐÁNH GIÁ ĐƯỢC**<br>*(Chờ duyệt Negative Oracle)* |
| **DoD 4** | Disclaimer y tế luôn hiển thị ở mọi phản hồi có cảnh báo (`disclaimer IS NOT NULL`). | • Đã xác minh qua `TC-DISC-01`, `test_interaction_checks_mixed_response` và các bài test mobile widget.<br>• Trong các ca và nhánh đã được kiểm thử trên Backend API và Mobile UI, disclaimer NFR03 đều hiển thị đúng từng ký tự bắt buộc. | **ĐÃ XÁC MINH TRONG CÁC CA/NHÁNH ĐÃ TEST**<br>*(Giới hạn trong phạm vi các ca test backend in-memory và widget test đã chạy; chưa khẳng định cho mọi phản hồi có thể có trên live)* | **ĐẠT (TRONG PHẠM VI TEST)** |
| **DoD 5** | Có báo cáo nghiệm thu kiểm thử chi tiết bàn giao cho Product Owner / Mentor. | • Văn bản báo cáo này (`PB24_Test_Report.md`) được lập đầy đủ số liệu, lệnh chạy, ma trận truy vết, benchmark và đối chiếu DoD chi tiết phục vụ bàn giao nghiệm thu.<br>• Hiện tại đã hoàn tất khâu lập báo cáo kỹ thuật; đang chờ quy trình bàn giao chính thức và xác nhận/ký duyệt từ Product Owner và Mentor. | **ĐÃ LẬP BÁO CÁO, CHỜ BÀN GIAO / XÁC NHẬN PO-MENTOR**<br>*(Báo cáo kỹ thuật đã sẵn sàng; chưa có biên bản ký nhận chính thức từ PO/Mentor)* | **ĐÃ LẬP (CHỜ XÁC NHẬN)** |

---

## 7. Các Khoảng Trống & Phụ Thuộc Kỹ Thuật Chưa Đóng (Open Dependencies)

1. **Khoảng trống Cặp tương tác Mức độ 1 (Severity 1):**
   - Toàn bộ 10 ca y văn hiện tại chỉ bao phủ Severity 2, 3, 4. Dự án **hoàn toàn thiếu ca tương tác Mức độ 1 (Nhẹ/Minor)** do tài liệu Task 4.01 không cung cấp. Cần Dược sĩ lâm sàng bổ sung cặp tương tác Mức 1 có trích dẫn y văn.
2. **Khoảng trống Danh mục Đối chứng Âm tính (Negative Oracle):**
   - Hiện mới có 5 ca candidate trích từ phác đồ Bộ Y tế (thiếu tối thiểu 5 ca để đạt chỉ tiêu 10 ca âm tính của kế hoạch 4.03). Cần Hội đồng Dược phê duyệt danh mục thuốc phối hợp an toàn.
3. **Cổng Thẩm định Lâm sàng (Clinical Sign-off Gate):**
   - Task 4.01 chưa có biên bản thẩm định chính thức (Pharmacist Attestation) có chữ ký số. Cổng này chặn việc đóng DoD 2 và DoD 3 của Task 4.03.
4. **Cổng Kiểm thử Tích hợp Cơ sở Dữ liệu Cô lập (Isolated Live DB Harness Gate):**
   - Chưa thể tiến hành E2E test thật sự trên thiết bị Mobile và server DB do thiếu môi trường PostgreSQL test harness cô lập.

---

## 8. Kết Luận Nghiệm Thu & Khuyến Nghị

1. **Về mặt Kỹ thuật Phần mềm (Software Engineering):**
   - Thuật toán `InteractionEvaluator` (CD7), API Backend và giao diện Mobile đã được kiểm thử tự động hóa nghiêm ngặt (70 backend tests, 13 mobile tests, ruff check 100% PASS).
   - Hiệu năng hệ thống NFR01 đạt độ trễ cực thấp (p95 đạt 17.73 ms, tối đa 24.09 ms << 2,000 ms).
   - Cơ chế bảo vệ liều lượng, giao hoán, xử lý thiếu dữ liệu và khử trùng lặp theo cặp thuốc hoạt động đúng đặc tả.
2. **Về mặt Nghiệm thu Hoàn tất (DoD Acceptance):**
   - **KẾT LUẬN: TASK 4.03 VÀ CỤM PB24 CHƯA THỂ DÁN NHÃN HOÀN TẤT TOÀN BỘ (CHƯA DONE).**
   - Task 4.03 đã xác minh các tiêu chí kỹ thuật: DoD 1 (bộ test case chuẩn hóa), DoD 4 (disclaimer trong phạm vi các ca test), và DoD 5 (đã lập báo cáo kỹ thuật, chờ bàn giao/xác nhận PO-Mentor). Hai tiêu chí cốt lõi về chất lượng y tế lâm sàng (**DoD 2: True Positive 100%** và **DoD 3: False Positive 0%**) **chưa được chứng minh / chưa thể đánh giá được** do thiếu clinical sign-off từ Dược sĩ và danh mục negative oracle được duyệt; không thể nghiệm thu đóng task khi các tiêu chí này còn mở.
3. **Khuyến nghị bước tiếp theo:**
   - Chuyển giao báo cáo này cho Product Owner và Mentor xem xét.
   - Thúc đẩy việc Dược sĩ lâm sàng thẩm định 10 quy tắc ĐTĐ của Task 4.01 và bổ sung tối thiểu 5 ca âm tính + 1 ca Severity 1.
   - Thiết lập môi trường Docker PostgreSQL Test Harness cô lập để phục vụ kiểm thử tích hợp E2E trước khi phát hành phiên bản production.
