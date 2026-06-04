# Evidence Pack — Trip-Guilder-Bot (AI Weekend Planner cho Cặp đôi)

Tài liệu này lưu trữ các bằng chứng thực tế (evidence) định hình thiết kế MVP của Trip-Guilder-Bot.

## 1. Nhóm và track

**Tên nhóm:** Nhóm 3  
**Track:** AI for Travel & Hospitality  
**Product/app đã chọn:** Google Search (AI Overview) khi dùng để lên kế hoạch hẹn hò  
**Build slice đang nghĩ:** Trợ lý AI (ReAct Agent dùng DeepSeek-v4-flash) giúp cặp đôi lên lịch hẹn hò nhanh chóng tại Hà Nội. Tự động đề xuất lịch trình theo giờ, hiển thị lượng người dự kiến đi để tránh nơi quá tải, tích hợp bản đồ và xuất lịch Google Calendar, hỗ trợ kéo thả điều chỉnh trực quan.

## 2. Self-use evidence

Nhóm tự dùng Google Search với câu lệnh:  
`"lập lịch trình hẹn hò cuối tuần lãng mạn cho cặp đôi tại Hà Nội"`

![Google AI Overview hạn chế](evidence_image\ev1.png)

| Observation | Screenshot/link | Path liên quan | Điều học được |
|-------------|----------------|----------------|----------------|
| Google AI Overview chỉ trả về đoạn văn bản gợi ý rất ngắn, không thể hiện rõ vibe lãng mạn, không tích hợp bản đồ địa điểm, không ước lượng khoảng cách di chuyển, không có nút thêm lịch, và hoàn toàn không cho biết địa điểm có đang quá đông đúc hay không. | ![AI Overview text tĩnh](./screenshots/google-ai-overview-han-che.png) | Failure / Low‑confidence | AI hiện tại chỉ dừng ở mức sinh text tĩnh thô sơ. Người dùng vẫn phải tự đi kiểm tra thông tin địa điểm, tự copy-paste sang Maps và Calendar thủ công, rất dễ làm hỏng trải nghiệm hẹn hò riêng tư. |

## 3. User / review / social evidence

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|------------------------------|-------|-------------|-------------------|
| *“Kết quả tìm kiếm Google thường bị chiếm bởi quảng cáo, ưu tiên dịch vụ kiếm tiền… không được thiết kế để giúp người dùng thiết kế một itinerary phức tạp.”* | [Cheapest Destinations Blog](https://www.cheapestdestinationsblog.com/10-steps-to-plan-a-vacation-better-beyond-google/) | Blogger du lịch | Search trả về nội dung thương mại, quảng cáo dồn dập, không giúp lập kế hoạch lãng mạn thực tế. |
| *“Google đã tung thêm tính năng AI cho Search, Maps và Gemini để hỗ trợ lập kế hoạch kỳ nghỉ… người dùng chuyển sang ChatGPT để lên kế hoạch chuyến đi.”* | [TechCrunch](https://techcrunch.com/2025/03/27/google-rolls-out-new-vacation-planning-features-to-search-maps-and-gemini/) | Nhà báo công nghệ | Search truyền thống không đáp ứng được tính cá nhân hóa; người dùng cần công cụ tạo itinerary có thể chia sẻ, chỉnh sửa linh hoạt. |
| *“ChatGPT tốt cho brainstorming nhưng không kiểm tra giá vé, xác minh nhà hàng còn tồn tại, hoặc tạo itinerary có thể chia sẻ và chỉnh sửa cộng tác.”* | [Stippl](https://www.stippl.io/blog/best-ai-travel-planner-2026) | Người đánh giá travel planner | AI sinh text thuần túy chưa đủ; cần kết hợp dữ liệu thực tế (giở mở cửa, độ đông đúc) và các công cụ Calendar. |

---

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|------------------------|----------------------------|------------------|--------------------------------|
| **Stippl AI travel planner** | User nhập yêu cầu → AI tạo timeline chi tiết, hỗ trợ kéo thả sắp xếp lại, chia sẻ nhóm và hiển thị bản đồ. | Tích hợp lập lịch + kéo thả chỉnh sửa + hiển thị trực quan trên bản đồ. | ✅ Có – phiên bản đơn giản hóa: timeline kéo thả cập nhật giờ di chuyển + xuất Calendar. |
| **ChatGPT / Gemini** | Trả về văn bản gợi ý hành trình, không có tính năng tương tác kéo thả hay đồng bộ lịch. | AI tạo nội dung tốt nhưng cần thêm lớp ứng dụng tương tác để thực thi hóa kế hoạch. | ✅ Có – sử dụng DeepSeek làm bộ não sinh JSON, frontend hiển thị dạng tương tác. |
| **Google Maps (Lưu điểm)** | Cho phép lưu danh sách địa điểm hẹn hò yêu thích nhưng không sắp xếp theo lịch trình thời gian hợp lý. | Cần thuật toán hoặc AI Agent để xâu chuỗi các địa điểm thành một lộ trình di chuyển tối ưu nhất. | ✅ Có – tích hợp hiển thị marker bản đồ và tính toán sơ bộ khoảng cách/thời gian. |

---

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
1. Google AI Overview chỉ trả về văn bản tĩnh sơ sài, không có sự lãng mạn hay cá nhân hóa cho cặp đôi.
2. Không có tích hợp Maps để tối ưu hóa quãng đường di chuyển của xe máy/ô tô tại Hà Nội.
3. Thiếu tính năng kiểm tra lượng người dự kiến đến để thực hiện tránh nơi quá đông (crowd avoidance).
4. Không có nút xuất Calendar để lưu giữ lịch hẹn và thông báo nhắc nhở.

Insight:
Các cặp đôi đi hẹn hò cần một công cụ giúp tối giản hóa việc chọn quán và xếp lịch, giúp họ có một lộ trình di chuyển mượt mà, hợp vibe, và quan trọng nhất là tránh được việc xếp hàng chờ đợi chen chúc phá hỏng không khí lãng mạn.

Opportunity:
AI Agent có thể augment quy trình hẹn hò bằng cách:
- Hỏi làm rõ vibe mong muốn (Lãng mạn ấm cúng, Trải nghiệm độc đáo, Khám phá ẩm thực).
- Thiết lập itinerary chi tiết từng giờ di chuyển và hoạt động.
- Hiển thị bản đồ marker trực quan để cặp đôi dễ hình dung.
- Cung cấp chỉ số "số lượng người lập kế hoạch đi cùng thời điểm" (crowd avoidance) dựa trên dữ liệu hệ thống.
- Hỗ trợ kéo thả chỉnh sửa và xuất nhanh file .ics Calendar để lưu lại.
```

---

## 6. Evidence đổi SPEC như thế nào?

- [x] Đổi user chính (Từ gia đình/bạn bè chung chung sang Cặp đôi hẹn hò tại Hà Nội).
- [x] Đổi pain statement (Tập trung vào sự riêng tư, vibe phù hợp và tránh chen chúc đông đúc).
- [x] Đổi build slice (Tích hợp 4 ReAct Tools và hiển thị chỉ số đám đông).
- [x] Đổi Auto/Aug decision (Giữ Augmentation để user tự review và kéo thả điều chỉnh).
- [x] Đổi 4 paths (Đổi kịch bản test sang buổi hẹn hò của cặp đôi).
- [x] Đổi failure mode (Đề xuất quán thay thế cùng vibe khi địa điểm chính bị quá tải hoặc đóng cửa).
- [x] Đổi owner/test plan.

```text
Trước evidence, nhóm định xây dựng một chatbot gợi ý địa điểm du lịch chung chung tại Hà Nội.

Sau evidence, nhóm tập trung toàn bộ nguồn lực vào "Trợ lý lập lịch hẹn hò tương tác cho Cặp đôi", tích hợp hiển thị bản đồ trực quan, theo dõi lượng người dự kiến (crowd avoidance), hỗ trợ kéo thả điều chỉnh lịch trình và xuất Calendar nhằm giải quyết triệt để pain point đứt gãy workflow chuẩn bị hẹn hò của các cặp đôi.
```