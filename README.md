# 📚 DrugTime Documentation

Tài liệu thiết kế kiến trúc, hợp đồng API, kế hoạch triển khai và quy chuẩn an toàn dược lý cho dự án **DrugTime — Hệ thống nhắc thuốc thông minh & kiểm soát an toàn dược lý gia đình**.

---

## 🌿 Nhánh Hiện Tại: `feat/api-contract`
Nhánh này tập trung vào việc **chuẩn hóa và chốt hạ toàn diện Hợp đồng API v2.3 FINAL** giữa Backend, Mobile App (Flutter) và Admin Web (Next.js 14).

### 🎯 Những việc đã hoàn thành trong nhánh này:
1. **Thiết kế & Chốt 27 Điểm Thay Đổi Cốt Lõi:**
   - Bảo vệ quyền riêng tư & dữ liệu cá nhân theo **Nghị định 356/2025/NĐ-CP** (Consent tracking 3 mục đích, Data Portability async qua `202 Accepted`, Right to be Forgotten).
   - An toàn dược lý: **0% LLM trong an toàn thuốc** (Rule Engine Bảng C/D/E là deterministic thuần túy).
   - Cơ chế giám sát kép **Four-Eyes Post-Review** cho can thiệp khẩn cấp của Admin (hậu kiểm ≤ 24h bởi Admin thứ 2).
   - Chống brute-force mã Caregiver (rate-limit 5 lần sai/15p, tự hủy mã sau 10 lần sai toàn cục).
   - Chuẩn hóa header `X-Admin-Reason: <string>` (tối thiểu 10 ký tự) cho mọi thao tác can thiệp lâm sàng.
   - Chuẩn hóa Soft-Delete toàn bộ dữ liệu y khoa (`trang_thai: 'archived'`), HTTP DELETE thuần không body.
2. **Đặc Tả Chi Tiết 64 Endpoints RESTful:** Chuẩn hóa Response Envelope UTF-8 `{success, data, error, message}` và phân trang PaginationEnvelope.
3. **Đồng Bộ Schema OpenAPI 3.1:** Phục vụ sinh mã client tự động cho Frontend và Backend.

---

## 📂 Danh Mục Tài Liệu Chính (Document Catalog)

| Tài liệu | Mô tả chi tiết | Trạng thái |
|---|---|:---:|
| 📘 [`API_DESIGN.md`](./API_DESIGN.md) | Đặc tả chi tiết 64 endpoints RESTful theo 9 nhóm chức năng, quy chuẩn header, envelope lỗi và RBAC. | **v2.3 FINAL** |
| 📋 [`CHANGES_FROM_SPEC.md`](./CHANGES_FROM_SPEC.md) | Bảng đối chiếu chi tiết 27 điểm cải tiến/thay đổi so với bản đặc tả ban đầu kèm lý giải kỹ thuật. | **Hoàn thành** |
| 🧠 [`CONTEXT_CACHE.md`](./CONTEXT_CACHE.md) | Bộ nhớ đệm kiến trúc, context bàn giao giữa các phiên làm việc, ma trận RBAC và danh sách tài khoản mock test. | **v2.3 FINAL** |
| 🌐 [`openapi.json`](./openapi.json) | File đặc tả OpenAPI 3.1 JSON xuất tự động từ FastAPI backend, phục vụ Swagger / Postman. | **Đồng bộ** |
| 🗄️ [`drugtime-schema_v2.md`](./drugtime-schema_v2.md) | Thiết kế cơ sở dữ liệu quan hệ PostgreSQL / Supabase, quan hệ khóa ngoại và ràng buộc audit trail. | **v2.0** |
| 🏗️ [`drugtime_architecture_decisions_by_container.md`](./drugtime_architecture_decisions_by_container.md) | Quyết định kiến trúc phần mềm theo các Container C4 (Mobile, Web, Backend Gateway, Database, Storage). | **Đã duyệt** |
| 🛡️ [`drugtime_quality_attribute_scenarios_ban_chinh.md`](./drugtime_quality_attribute_scenarios_ban_chinh.md) | Kịch bản kiểm thử thuộc tính chất lượng (QA.01 – QA.10, NFR01 – NFR07: an toàn, hiệu năng, bảo mật). | **Chính thức** |
| 📊 [`DrugTime_Gantt_Chart.md`](./DrugTime_Gantt_Chart.md) | Kế hoạch tiến độ tổng thể các sprint, milestone và phân bổ nhân sự (kèm dashboard HTML & Mermaid). | **Sprint 1-4** |
| 📑 [`DrugTime_Project charter_21092026.docx`](./DrugTime_Project%20charter_21092026.docx) | Điều lệ dự án Capstone DrugTime (Mục tiêu, phạm vi, rủi ro, stakeholder). | **Bản ký** |

---

## 🛠️ Hướng Dẫn Sử Dụng & Bàn Giao
- **Để xem giao diện API trực quan:** Khởi chạy Backend (`cd ../backend && python main.py`) và truy cập [http://localhost:8000/docs](http://localhost:8000/docs).
- **Để cập nhật lại file OpenAPI khi sửa schema:** Chạy script re-export được hướng dẫn tại Mục 7 trong [`CONTEXT_CACHE.md`](./CONTEXT_CACHE.md).
