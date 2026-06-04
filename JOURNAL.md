# HACKATHON Journal — Team 006

> Ghi lại mỗi tuần: học được gì, khó khăn gì, quyết định gì, kế hoạch tiếp.

---

## HACKATHON Week 1 (Day 05 - Day 06): 04/06/2026 - 11/06/2026

### Mục tiêu tuần này
- [x] Khảo sát và thu thập bằng chứng (evidence) về hạn chế của Google AI Overview trong việc lên kế hoạch du lịch/hẹn hò tại Hà Nội.
- [x] Chốt đối tượng mục tiêu MVP: Cặp đôi hẹn hò tại Hà Nội (dating or married, không dắt theo con nhỏ).
- [x] Thiết kế 4 UX Paths (Happy, Low-Confidence, Failure, Correction) để quản trị sự bất định của AI.
- [x] Thiết kế chi tiết kiến trúc MVP kết hợp Next.js, FastAPI, SQLite seed database và LangGraph ReAct Agent (DeepSeek-v4-flash).
- [ ] Khởi tạo khung dự án Next.js & FastAPI backend, thiết kế giao diện lãng mạn.

### Đã hoàn thành
- [x] Tài liệu hóa toàn bộ spec nhóm: [thin-spec-template.md](file:///d:/Personlich/AIO/AIO2025%20-%20Main/_2026_Research/VIN%20Practitioner/Trip-Guilder-Bot/02-group-spec/thin-spec-template.md), [synthesis-decide-toolkit.md](file:///d:/Personlich/AIO/AIO2025%20-%20Main/_2026_Research/VIN%20Practitioner/Trip-Guilder-Bot/02-group-spec/synthesis-decide-toolkit.md), [evidence-pack-template.md](file:///d:/Personlich/AIO/AIO2025%20-%20Main/_2026_Research/VIN%20Practitioner/Trip-Guilder-Bot/02-group-spec/evidence-pack-template.md).
- [x] Hoàn thiện tài liệu kiến trúc [ARCHITECTURE.md](file:///d:/Personlich/AIO/AIO2025%20-%20Main/_2026_Research/VIN%20Practitioner/Trip-Guilder-Bot/ARCHITECTURE.md) mô tả luồng xử lý của LangGraph Agent, schema cơ sở dữ liệu SQLite và danh mục 4 ReAct Tools.
- [x] Viết chi tiết đặc tả tính năng trong [SPECS.md](file:///d:/Personlich/AIO/AIO2025%20-%20Main/_2026_Research/VIN%20Practitioner/Trip-Guilder-Bot/SPECS.md) bao gồm: Chat Vibe Clarification, Crowd Avoidance, timeline kéo thả, Leaflet JS Map, và kết xuất file lịch `.ics`.
- [x] Cập nhật tài liệu hướng dẫn phát triển trong [CONTEXT.md](file:///d:/Personlich/AIO/AIO2025%20-%20Main/_2026_Research/VIN%20Practitioner/Trip-Guilder-Bot/CONTEXT.md) làm dữ liệu ngữ cảnh chất lượng cho CODEX.

### Khó khăn & Giải pháp

| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Google AI Overview chỉ trả gợi ý text tĩnh thô sơ, không tương tác được. | Thiết kế timeline kéo thả reorder trực tiếp, tự động tính toán lại giờ di chuyển. | Tăng tính kiểm soát (augmentation), người dùng dễ dàng tinh chỉnh lịch hẹn hò theo ý muốn. |
| Nguy cơ quán hẹn hò quá đông đúc làm hỏng không khí lãng mạn riêng tư. | Tích hợp chỉ số "Số người lập kế hoạch đi cùng lúc" (Crowd Level) và cơ chế tự động gợi ý quán thay thế cùng vibe. | Giúp cặp đôi chủ động né tránh đám đông (crowd avoidance). |
| Tránh tình trạng ảo ảnh địa điểm (hallucination) từ mô hình LLM. | Sử dụng mô hình hybrid: SQLite seed database chứa ~80 địa điểm tuyển chọn ở Hà Nội làm cốt lõi + live API làm giàu thông tin. | Đảm bảo 100% địa điểm đề xuất là chính xác và có thực. |

### Bài học
- Thiết kế sản phẩm AI đòi hỏi tư duy quản trị sự bất định (uncertainty) chứ không phải cố gắng xây dựng một hệ thống luôn đúng. Việc có các đường xử lý lỗi (error routing) rõ ràng giúp giữ vững niềm tin của người dùng.
- Bắt đầu bằng Augmentation (Copilot/Gợi ý) là nước đi an toàn và thực dụng trước khi tích hợp hệ thống tự động hóa đặt chỗ.

### Kế hoạch Mở rộng
- [ ] Khởi tạo mã nguồn khung Frontend Next.js và Backend FastAPI.
- [ ] Thiết lập SQLite database và import ~80 địa điểm hẹn hò lãng mạn, trải nghiệm tại Hà Nội.
- [ ] Viết prompt và cấu hình ReAct Agent điều khiển 4 tools trên LangGraph.
- [ ] Code giao diện kéo thả timeline và tích hợp Leaflet JS hiển thị sơ đồ di chuyển.
