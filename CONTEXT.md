# Context: Trip-Guilder-Bot (AI Weekend Planner cho Cặp đôi)

Tài liệu này đóng vai trò làm **Bản Hướng dẫn Chất lượng & Lập trình (Quality Context & Developer Guide)** cho **CODEX** (hoặc bất kỳ AI agent nào). Tài liệu phác thảo triết lý xây dựng ứng dụng AI trong môi trường không chắc chắn, thông số sản phẩm dành cho **Trip-Guilder-Bot**, kiến trúc hệ thống, 4 UX paths, và các cột mốc triển khai (milestones).

---

## 📖 1. Core Philosophy: Designing AI Products for Uncertainty

Ứng dụng AI khác với phần mềm truyền thống ở tính **xác suất** (probabilistic) thay vì quyết định luận (deterministic). Phát triển sản phẩm AI thực chất là **quản lý rủi ro, phân luồng lỗi (error routing), và tạo vòng lặp phản hồi (feedback loops)**.

### 1.1 Ba tầng không chắc chắn (Three Layers of Uncertainty)
1. **Input Uncertainty**: Người dùng nhập các yêu cầu mơ hồ hoặc thiếu thông tin (ví dụ: *"hẹn hò cuối tuần"* - thiếu vibe, ngân sách, phương tiện, thời gian).
2. **Process Uncertainty**: Agent diễn dịch sai yêu cầu, gọi công cụ (tool) gặp lỗi, hoặc bị giới hạn ngữ cảnh (context window).
3. **Output Uncertainty**: Mô hình bị ảo ảnh (hallucination), gợi ý địa điểm đã đóng cửa, hoặc đề xuất quán quá đông đúc làm hỏng không khí hẹn hò riêng tư.

### 1.2 Vòng đời xử lý lỗi: Detect → Route → Recover → Learn
*   **Detect**: Phát hiện đầu vào có độ tự tin thấp (vague prompt) hoặc lỗi thực thi công cụ (API error, database empty).
*   **Route**: Chuyển hướng xử lý sang luồng an toàn (Clarification prompt, fallback template, hiển thị UI lựa chọn thay thế).
*   **Recover**: Cung cấp công cụ trực quan để người dùng khôi phục và chỉnh sửa (kéo thả thay đổi giờ, nút đổi địa điểm cùng vibe).
*   **Learn**: Thu thập hành động chỉnh sửa của người dùng thành tín hiệu học máy (ghi log console dạng JSON) để liên tục cải tiến hệ thống prompt và seed database.

### 1.3 Automation vs. Augmentation
*   **Augmentation (Selected Path)**: AI đóng vai trò đề xuất lịch trình nháp. Người dùng là người duyệt, chỉnh sửa và quyết định cuối cùng.
    *   *Tại sao?* Buổi hẹn hò của cặp đôi mang tính riêng tư cao. Một gợi ý không hợp vibe hoặc một quán quá đông đúc có thể phá hỏng cảm xúc cả ngày. Chi phí để người dùng chỉnh sửa/bác bỏ gợi ý của AI là cực kỳ thấp nếu UI/UX hỗ trợ kéo thả tiện lợi.
*   **Agency Progression**: Bắt đầu bằng Augmentation (V1 Suggestion & V2 Copilot) trước khi nâng cấp lên V3 (Automation - tự động đặt chỗ) khi đã thu thập đủ dữ liệu tương tác thực tế.

---

## 🛠️ 2. Product Specification & Build Slice (AI Weekend Planner)

### 2.1 Target User & Pain Statement
*   **Target User**: Các cặp đôi tại Hà Nội (đang hẹn hò hoặc đã kết hôn, không dắt theo con nhỏ) đang lên kế hoạch đi chơi/hẹn hò cuối tuần.
*   **Pain Statement (Grounded in Evidence)**:
    *   Google AI Overview trả về văn bản lịch trình tĩnh và cực kỳ sơ sài, không có bản đồ di chuyển, không có lịch nhắc nhở, và không quan tâm đến vibe hẹn hò hay độ đông đúc của quán.
    *   Người dùng phải liên tục nhảy qua lại giữa Google Search, Maps, Facebook/Tiktok review, Calendar và các app nhắn tin để bàn bạc và chốt lịch.
    *   Cặp đôi sợ nhất cảnh đến nơi lãng mạn nhưng quán quá đông phải xếp hàng chờ đợi lâu.
*   **Analog Pattern (Inspiration)**: *Stippl AI Travel Planner* (chuyển đổi text thành timeline trực quan, kéo thả reorder, đồng bộ maps & calendar).

### 2.2 The Build Slice (Hackathon Scope)
MVP prototype tập trung vào vòng lặp khép kín:
> **User nhập tiêu chí hẹn hò** $\rightarrow$ **ReAct Agent (DeepSeek-v4-flash) gọi Tools tạo timeline chi tiết kèm chỉ số độ đông đúc (crowd level)** $\rightarrow$ **Bản đồ tương tác hiển thị markers vị trí** $\rightarrow$ **User kéo thả để đổi giờ hoặc xóa/đổi điểm** $\rightarrow$ **Xuất lịch hẹn hò (.ics)** $\rightarrow$ **Hệ thống in event log JSON ra console**.

---

## 🎨 3. The Four UX Paths & Fallback Designs

| Path | Scenario | System UX Response |
| :--- | :--- | :--- |
| **1. Happy Path** | User nhập đầy đủ thông tin (e.g., *“Cặp đôi, vibe lãng mạn riêng tư, đi chiều tối thứ 7, xe máy”*). | Agent gọi `get_favourable_place` truy vấn SQLite seed DB & API, trả về lịch trình 3 điểm kèm giờ di chuyển, hiển thị lượng người dự kiến (để tránh quá đông), vẽ sơ đồ lên bản đồ, nút xuất Calendar hoạt động. |
| **2. Low‑Confidence Path** | User nhập mơ hồ (e.g., *“đi hẹn hò đi”*, *“đi đâu cũng được”*). | Agent nhận diện độ tự tin thấp. Hệ thống hiển thị Clarification UI gồm 3 nút chọn vibe: *(1) Lãng mạn & Riêng tư, (2) Năng động & Trải nghiệm mới, (3) Ẩm thực & Phố xá*. |
| **3. Failure Path** | User nhập yêu cầu không tồn tại/dị biệt (e.g., *“đi uống cafe ngắm khủng long bay ở Hà Nội”*). | Agent phản hồi tế nhị: *"Không tìm thấy địa điểm phù hợp."* và kích hoạt fallback hiển thị 3 địa điểm hẹn hò lãng mạn kinh điển: **Hồ Tây, Cầu Long Biên, Cafe Yên**. |
| **4. Correction Path** | User kéo thả thẻ thay đổi thứ tự hoạt động hoặc bấm nút xóa/thay thế địa điểm. | Hệ thống tự động tính toán lại thời gian di chuyển trên timeline, vẽ lại đường đi trên bản đồ, và in sự kiện chỉnh sửa dạng JSON ra console của trình duyệt. |

---

## 🏗️ 4. System Architecture & Data Schema

### 4.1 Technology Stack
1.  **Frontend**: React / Next.js, Premium Vanilla CSS.
    *   *Design Aesthetics*: Sử dụng tông màu lãng mạn (pastel, dark mode sang trọng, rose/gold accents), font chữ Outfít hoặc Inter, các micro-animations mượt mà, thiết kế dạng card kính mờ (glassmorphism). Không sử dụng các layout thô sơ mặc định của trình duyệt.
2.  **Backend & AI Engine**:
    *   FastAPI Backend đóng vai trò API Gateway.
    *   **LangGraph ReAct Agent** kết hợp mô hình **DeepSeek-v4-flash** làm bộ não điều hành, thực thi hội thoại và gọi Tools.
3.  **Database & Live API Integration**:
    *   **SQLite** lưu seed data ~80 địa điểm hẹn hò tuyển chọn (Hanoi spots).
    *   Tích hợp live API Google Maps (lấy địa chỉ, trạng thái mở cửa, hình ảnh) và Google Search làm fallback làm phong phú thông tin.
    *   Chỉ số **Crowd Avoidance**: Thống kê số lượng user lập kế hoạch check-in cùng khung giờ trên hệ thống.
4.  **Calendar Integration**:
    *   Xuất file `.ics` chuẩn để người dùng nạp trực tiếp vào Apple Calendar / Google Calendar.

### 4.2 Learning Loop Event Log Schema
Mỗi khi user thay đổi timeline (kéo thả, xóa, thay điểm), frontend gửi log JSON sau về backend và in ra console:
```json
{
  "timestamp": "2026-06-04T09:40:00Z",
  "event_type": "itinerary_reordered | spot_deleted | spot_replaced | fallback_triggered",
  "data": {
    "spot_id": "cafe_yen_giang_vo",
    "old_time_slot": "15:00 - 17:00",
    "new_time_slot": "16:00 - 18:00",
    "reason_if_any": "user_drag_drop",
    "user_context": {
      "vibe": "cozy_and_quiet",
      "num_people": 2
    }
  }
}
```

---

## 🎯 5. System Design Milestones & Definition of Done (DoD)

### Milestone 1: Setup Dự án, Layout & Design System
*   [ ] Khởi tạo khung dự án Next.js kết hợp FastAPI backend.
*   [ ] Thiết lập Design System lãng mạn trong CSS (Outfít font, gradients mềm mại, glassmorphism cards).
*   *DoD Check*: UI đẹp mắt, responsive, các nút hover có micro-animations mượt mà.

### Milestone 2: Phát triển ReAct Agent & 4 Tools (Milestone 2 & 3 gộp)
*   [ ] Xây dựng LangGraph ReAct agent sử dụng DeepSeek-v4-flash.
*   [ ] Hiện thực hóa 4 Tools: `get_new_experience`, `get_favourable_place`, `get_current_trend`, `map_and_export_trip`.
*   [ ] Setup SQLite seed database với các bảng điểm hẹn hò tuyển chọn tại Hà Nội.
*   *DoD Check*: Agent gọi đúng các Tool lọc dữ liệu dựa trên vibe yêu cầu của user và trả về JSON lịch trình có cấu trúc.

### Milestone 3: Bản đồ Tương tác & Tránh Đông đúc (Path 1 & 3)
*   [ ] Tích hợp Leaflet JS hoặc Google Maps iframe vẽ lộ trình di chuyển.
*   [ ] Hiển thị thông số lượng người dự kiến (crowd level) trên thẻ lịch trình.
*   [ ] Thực thi Path 3 (Failure Fallback): Khi không có điểm phù hợp, hiển thị 3 điểm hẹn hò kinh điển.
*   *DoD Check*: Tìm kiếm lãng mạn ra đúng bản đồ marker + timeline chi tiết; tìm kiếm dị biệt kích hoạt fallback gợi ý 3 điểm.

### Milestone 4: Kéo thả Timeline & Ghi nhận Log (Path 4)
*   [ ] Hiện thực hóa tương tác kéo thả reorder các thẻ timeline hoạt động của cặp đôi.
*   [ ] Tự động tính toán lại khoảng thời gian rảnh/giờ di chuyển khi timeline thay đổi.
*   [ ] Bắn event log JSON ra Console của trình duyệt theo đúng schema ở Section 4.2.
*   *DoD Check*: Kéo thả swap vị trí cafe và ăn tối lập tức cập nhật lại thứ tự di chuyển và in ra JSON log chuẩn xác.

### Milestone 5: Kết xuất Calendar & QA cuối cùng
*   [ ] Hiện thực hóa nút xuất Calendar sinh file `.ics` tải xuống trực tiếp.
*   [ ] Chạy thử nghiệm toàn bộ 4 Paths và kiểm tra giao diện trên mobile.
*   *DoD Check*: File `.ics` tải xuống thành công, import vào Google/Apple Calendar hiển thị đúng giờ và tên địa điểm hẹn hò.
