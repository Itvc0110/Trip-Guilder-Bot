# Thin SPEC — Trip-Guilder-Bot (AI Weekend Planner)

Thin SPEC này là bản cam kết thiết kế chi tiết để hiện thực hóa MVP của Trip-Guilder-Bot.

## 1. Track, product/app và user

**Track:** AI for Travel & Hospitality  
**Product/app thật:** Google Search (AI Overview) – dùng để lên kế hoạch đi chơi  
**User cụ thể:** Các cặp đôi tại Hà Nội (đang hẹn hò hoặc đã kết hôn, không dắt theo con nhỏ) đang lên kế hoạch cho một buổi đi chơi/hẹn hò cuối tuần.  
**Nhóm có phải user thật không? Nếu không, khác ở đâu?**  
Có. Các thành viên trong nhóm đều từng tự lên kế hoạch hẹn hò hoặc đi chơi cuối tuần cùng người yêu/bạn đời tại Hà Nội và gặp khó khăn trong việc tìm địa điểm lãng mạn, mới lạ hoặc tránh những nơi quá đông đúc.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|----------|-------|----------------------------|--------------------|
| Google AI Overview trả về đoạn văn bản lịch trình rất ngắn (chỉ buổi sáng), không Maps, không Calendar, không hỏi lại sở thích. | Self-use (screenshot `google-ai-overview-han-che.png`) | User chỉ nhận được gợi ý dạng text tĩnh, không thể dùng ngay cho buổi hẹn hò, phải tự tra Maps và nhập Calendar thủ công. | Tích hợp Maps và nút xuất Calendar. Thêm cơ chế hỏi lại để thu thập sở thích, vibe buổi hẹn hò (lãng mạn, ấm cúng, phiêu lưu). |
| *“Google đã tung thêm tính năng AI cho Search, Maps và Gemini… người dùng chuyển sang ChatGPT để lên kế hoạch chuyến đi.”* | TechCrunch (2025) | Search truyền thống không đáp ứng; cặp đôi cần công cụ tạo itinerary hẹn hò có thể chia sẻ, chỉnh sửa và tối ưu hóa thời gian di chuyển. | Tập trung vào khả năng chỉnh sửa lịch trình trực quan, đề xuất tuyến đường và hiển thị bản đồ trực tiếp. |
| *“ChatGPT tốt cho brainstorming nhưng không tạo itinerary có thể chia sẻ và chỉnh sửa cộng tác.”* | Stippl | AI sinh text thuần chưa đủ; cần tích hợp dữ liệu thực tế (địa điểm thực) và các công cụ xuất lịch. | Cho phép user chỉnh sửa itinerary trực tiếp, tích hợp cơ chế check số lượng người lập kế hoạch đi để tránh các điểm quá tải. |

## 3. Pain statement

```text
User (cặp đôi tại Hà Nội) đang lên kế hoạch hẹn hò/đi chơi cuối tuần,
vì Google AI Overview chỉ trả về gợi ý dạng text tĩnh, không có bản đồ, không thể thêm vào lịch, không hiển thị lượng người để tránh nơi quá đông,
dẫn tới người dùng phải tự tra cứu Maps, tự liên hệ kiểm tra hoặc lo lắng về việc chen chúc, mất đi không khí lãng mạn riêng tư.
Bằng chứng chính là ảnh chụp màn hình Google AI Overview với lịch trình sơ sài, thiếu các công cụ tương tác thực tế cho cặp đôi.
```

## 4. Build Slice (MVP Scope)

```text
Cho các cặp đôi ở Hà Nội đang lên kế hoạch hẹn hò cuối tuần nhưng chỉ nhận được gợi ý dạng text từ Google AI Overview,
prototype sẽ sử dụng ReAct Agent (DeepSeek-v4-flash) với 4 công cụ (New Experience, Favourable Place, Current Trend, Map & Export) để:
1. Nhận yêu cầu và hỏi lại nếu thiếu thông tin (vibe hẹn hò, ngân sách, phương tiện).
2. Tạo lịch trình chi tiết theo khung giờ, hiển thị lượng người dự kiến lập kế hoạch đi cùng thời điểm để tránh quá tải (crowd avoidance).
3. Hiển thị các địa điểm hẹn hò trên bản đồ (Leaflet JS/iframe Google Maps).
4. Cho phép kéo thả chỉnh sửa thứ tự hoặc thay thế địa điểm, xuất lịch sang Google Calendar (.ics) và ghi nhận log chỉnh sửa.
```

## 5. Auto/Aug decision

Chọn một:

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:**  
Buổi hẹn hò của cặp đôi mang tính cá nhân hóa cực kỳ cao, phụ thuộc vào tâm trạng, thời tiết và không gian (vibe). AI không nên tự động đặt chỗ hay chốt lịch cứng nhắc. User cần giữ vai trò duyệt, tinh chỉnh và quyết định cuối cùng.

**Human role:** reviewer, decider, rescuer, trainer

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|------|------------------------------|
| Happy | User nhập đầy đủ thông tin (vibe: lãng mạn riêng tư, thời gian: chiều-tối thứ 7, phương tiện: xe máy). AI Agent dùng các công cụ lọc từ seed database (kết hợp API) trả về lịch trình 3 điểm (cafe view hồ, ăn tối steakhouse, dạo phố cổ) kèm giờ giấc, hiển thị số người dự kiến để tránh quá tải, hiển thị bản đồ, nút "Thêm vào Calendar". |
| Low‑confidence | User trả lời mơ hồ ("đi đâu cũng được", "gợi ý gì cũng được"). AI phát hiện mơ hồ và hiển thị Clarification UI với 3 nút lựa chọn vibe hẹn hò: *(1) Lãng mạn & Riêng tư, (2) Năng động & Trải nghiệm mới, (3) Ẩm thực & Phố xá*. |
| Failure | User nhập yêu cầu quá dị biệt không có trong DB hoặc API (ví dụ: "nhà hàng phục vụ thịt chim cánh cụt ở Hà Nội"). AI thông báo lịch sự không tìm thấy và kích hoạt fallback: gợi ý 3 địa điểm hẹn hò lãng mạn phổ biến nhất (Hồ Tây, Cầu Long Biên, Cafe Yên) kèm câu hỏi "Bạn có muốn thử các địa điểm hẹn hò được ưa thích này không?". |
| Correction | User kéo thả đổi thứ tự (muốn ăn tối trước rồi đi cafe sau) hoặc bấm nút xóa/thay thế địa điểm. AI tự động cập nhật lại thời gian di chuyển, khung giờ trên timeline, cập nhật bản đồ, và in log sự kiện dạng JSON ra Console của trình duyệt để học hỏi hành vi. |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user yêu cầu một không gian hẹn hò cụ thể nhưng địa điểm đó đã đóng cửa hoặc quá tải nghiêm trọng, dẫn đến buổi hẹn hò bị hỏng và cặp đôi thất vọng.
Prototype sẽ xử lý bằng cách:
1. Sử dụng live API để kiểm tra trạng thái hoạt động thực tế.
2. Hiển thị "lượng người dự kiến check-in" dựa trên số lượng người dùng đang lập kế hoạch đến địa điểm đó trong ngày qua hệ thống.
3. Nếu một địa điểm bị đánh dấu quá tải hoặc đóng cửa, Agent tự động đề xuất một địa điểm thay thế tương đương (cùng vibe, cùng khu vực) ngay lập tức.
Owner kiểm thử path này là Đinh Nhật Thành.
```

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|------------|----------------|-------------------------------|
| Nguyễn Anh Quân | Research / evidence | File evidence-pack.md hoàn chỉnh, ảnh screenshot, link nguồn |
| Nguyễn Khánh Toàn | SPEC (thin-spec.md) | File thin-spec.md hoàn chỉnh, 4 paths, failure mode |
| Phạm Thị Linh Chi | Prototype (UI + logic gọi AI) | Code prototype chạy được, input → AI → output, hiển thị Maps mock, nút Calendar |
| Lưu Thiện Việt Cường | Hỗ trợ prototype / tích hợp Maps & Calendar mock | Code phần hiển thị địa điểm trên iframe Maps, tạo mock link Calendar |
| Đinh Nhật Thành | Test / failure path (chạy code test) | Prompt test, ảnh chụp happy path và failure path, log correction, đảm bảo các path hoạt động |
| Phạm Trung Hiếu | Demo script + repo | File demo-slides.pdf, repo GitHub public, chuẩn bị narrative demo, quản lý nhóm |
