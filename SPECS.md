# Specific Features Specification — Trip-Guilder-Bot

Tài liệu này đặc tả chi tiết các tính năng cụ thể (Specific Features) của Trip-Guilder-Bot phục vụ MVP dành cho đối tượng Cặp đôi hẹn hò tại Hà Nội.

---

## 1. Chat & Clarification Interface (Khung Chat & Bộ lọc Vibe)

### Giao diện trò chuyện (GPT-like Chat)
- Khung chat chính cho phép người dùng nhập yêu cầu tự do (ví dụ: *"lên lịch đi chơi tối thứ Bảy"*).
- Hỗ trợ hiển thị các bong bóng gợi ý sẵn ngay trên thanh chat để người dùng nhấp nhanh.

### Clarification Wizard (Low-Confidence Path)
- Trực quan hóa khi Agent phát hiện đầu vào có độ tự tin thấp hoặc quá mơ hồ.
- Hệ thống sẽ hiển thị một hộp thoại lựa chọn nhanh (Wizard) với 3 nút bấm tương ứng với 3 Vibe hẹn hò của cặp đôi:
  1. **Lãng mạn & Riêng tư**: Thích hợp cho các buổi hẹn hò ấm cúng, quán cafe khuất hoặc nhà hàng view đẹp ngắm hoàng hôn.
  2. **Năng động & Trải nghiệm mới**: Dành cho cặp đôi thích khám phá quán mới mở, khu tổ hợp nghệ thuật, workshop làm đồ gốm/nến thơm.
  3. **Ẩm thực & Phố xá**: Dành cho food tour phố cổ, dạo phố đi bộ, ăn vặt vỉa hè.

---

## 2. AI Itinerary & Timeline Generator (Bộ tạo Lịch trình)

### Sinh lịch trình dạng Thẻ (Itinerary Cards)
- Agent (DeepSeek-v4-flash) sử dụng các Tool truy vấn SQLite và API để xếp lịch trình dạng trục thời gian (timeline).
- Mỗi địa điểm được hiển thị thành một thẻ hoạt động chi tiết bao gồm:
  - **Khung giờ**: Ví dụ `15:00 - 17:00` (bao gồm cả ước lượng thời gian di chuyển giữa các điểm).
  - **Tên địa điểm & Ảnh**: Rút trích từ seed DB hoặc API.
  - **Mô tả ngắn**: Lý do Agent đề xuất địa điểm này cho cặp đôi.
  - **Vibe badge**: Gắn nhãn vibe (Lãng mạn, Năng động, Vỉa hè...).
  - **Nút tương tác**: Nút Xóa (Delete) và Thay thế (Replace).

---

## 3. Crowd Avoidance System (Kiểm soát độ đông đúc)

### Trực quan hóa mật độ (Crowd Level Badge)
- Mỗi thẻ địa điểm hiển thị một chỉ số: **"Số lượng người lập kế hoạch đi"** (ví dụ: *"12 cặp đôi đã lên lịch đi lúc 19:00"*).
- Chỉ số này được tính bằng cách truy vấn số lượng người dùng đang lưu lịch trình chứa địa điểm đó trong cùng khung giờ trên hệ thống.

### Graceful Fallback khi quá tải
- Nếu chỉ số vượt ngưỡng cảnh báo (ví dụ >25 người tại một quán cafe nhỏ), thẻ địa điểm sẽ hiển thị cảnh báo màu cam: *"Quán có thể rất đông vào khung giờ này"*.
- Agent tự động đề xuất một tùy chọn thay thế cùng vibe, cùng quận để cặp đôi chủ động né tránh đám đông.

---

## 4. Interactive Maps (Bản đồ tương tác)

### Leaflet JS / Google Maps Iframe Integration
- Bản đồ hiển thị ở khung bên phải màn hình (có thể thu nhỏ/phóng to).
- Renders tự động các marker vị trí theo đúng thứ tự của timeline (được đánh số `1`, `2`, `3`...).
- Khi người dùng di chuột qua thẻ trên timeline, marker tương ứng trên bản đồ sẽ phát hiệu ứng pulse hoặc mở pop-up thông tin quán.
- Vẽ đường đi kết nối đơn giản giữa các điểm để biểu diễn lộ trình di chuyển.

---

## 5. Timeline Correction & Drag-and-Drop (Chỉnh sửa lịch trình)

### Kéo thả đổi thứ tự (HTML5 Drag & Drop)
- Người dùng có thể giữ và kéo thả các thẻ để đổi thứ tự các hoạt động (ví dụ: kéo quán cafe tối lên trước bữa tối).
- **Recalculation engine**: Hệ thống tự động tính toán lại thời gian di chuyển và cập nhật lại khung giờ trên các thẻ timeline ngay lập tức mà không cần gọi lại AI.

### Thay thế nhanh (Quick Replace)
- Khi bấm nút "Replace" trên thẻ, hệ thống hiển thị danh sách 3 địa điểm thay thế phù hợp nhất (cùng vibe, gần khu vực đó).
- Người dùng chỉ cần nhấp chọn để thay thế ngay lập tức vào timeline.

---

## 6. Feedback Loop & Console Event Logging (Ghi nhận hành vi)

- Ghi lại mọi hành động chỉnh sửa của người dùng thành cấu trúc JSON và in ra developer console:
  - `timestamp`: Thời gian thao tác.
  - `event_type`: Loại hành động (`itinerary_reordered`, `spot_deleted`, `spot_replaced`).
  - `data`: Chi tiết thay đổi (quán cũ, quán mới, khung giờ cũ, khung giờ mới).
- Log này đồng thời được gửi về api `/api/log` để lưu trữ làm cơ sở dữ liệu huấn luyện (fine-tune) prompt và tối ưu seed database.

---

## 7. Google Calendar & ICS Export (Kết xuất Lịch trình)

- **Tải file .ics**: Tạo và tải xuống file lịch `.ics` tương thích tốt với Apple Calendar, Google Calendar, Outlook.
- **Mock Calendar Sync**: Nút "Thêm vào Google Calendar" mở ra tab mới dẫn tới liên kết tạo sự kiện Google Calendar pre-filled các thông tin: Tên hoạt động, Vị trí (địa chỉ quán), Khung giờ hẹn hò, và ghi chú mô tả.
