# DrugTime — Quyết định kiến trúc và tactic theo container

| Container | Quyết định | Tactic áp dụng | QA |
|---|---|---|---|
| **Mobile App** | Nhắc thuốc bằng local notification, không qua server | Degradation (không phụ thuộc mạng/server) | QA.06, 08 |
| | Lưu lịch và xác nhận liều cục bộ, đồng bộ sau (outbox + `client_uuid`) | Redundancy of data, Recover (retry) | QA.08, 05 |
| | Simple Mode: theme riêng, nút xác nhận ≤ 2 chạm | Separate user interface, Minimize steps | QA.03 |
| **Backend API** | Modular monolith, `router → service → repository` | Increase cohesion, Prevent ripple | QA.10 |
| | Một điểm kiểm soát truy cập: kiểm tra link, consent, rồi ghi `access_logs` | Authorize actors, Limit access, Maintain audit trail, Detect attacks | QA.01, 02, 09 |
| | Bộ kiểm tra tương tác là hàm thuần, rule-based, không LLM | Deterministic logic, Testability (tách logic khỏi hạ tầng) | QA.04 |
| | Interface `Notifier` (FCM, Zalo thêm sau) | Use an intermediary, Defer binding | QA.11 |
| | Ghi liều idempotent bằng `client_uuid` | Reduce overhead, Retry an toàn | QA.05, 08 |
| **Worker (RQ)** | Phát hiện bỏ lỡ liều (có thời gian ân hạn), gửi FCM cho người thân | Introduce concurrency (xử lý nền) | QA.05, 08 |
| **Redis** | Chỉ làm hàng đợi cho Worker, không chứa audit log | Introduce concurrency | QA.09 |
| **Supabase** | Bật RLS, chỉ API/Worker truy cập | Limit exposure, Authorize actors | QA.02 |
| | `consents` và `access_logs` chỉ thêm, không sửa/xóa | Maintain audit trail | QA.01, 09 |
| | Nhóm bệnh dùng bảng lookup thay vì ENUM | Defer binding (data-driven) | QA.10 |
| **Admin Web** | Chỉ gọi API; thêm catalog và nhóm bệnh qua dashboard | Limit exposure, Defer binding | QA.10 |
| **Hạ tầng** | `/health` cộng monitor ngoài mỗi ≤ 1 phút | Detect faults (ping/echo), Recover (Render restart) | QA.07 |

## Lưu ý

1. Mobile gánh QA.06 và QA.08, nhưng Proposal chưa mô tả component nội bộ của Mobile.
2. Render free tier có thể làm QA.05 và QA.07 khó đạt; nên ghi rõ giả định trong ADD.
3. Cần bổ sung module `consent`, `family`, `ai_meal` và bỏ `partner` (Phase 2) trong Proposal §12.2.
