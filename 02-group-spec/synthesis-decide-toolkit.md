# Synthesis & Decide — Từ Evidence đến Build Slice

## 1. Gom evidence thành cụm

Không gom theo feature, gom theo workflow/pain.

### Cụm 1 — Google AI Overview chỉ trả text, thiếu tương tác & tích hợp

Self-use evidence cho thấy Google AI Overview trả về đoạn văn bản lịch trình rất ngắn (chỉ buổi sáng), không có nút tương tác, không hiển thị bản đồ, không ước lượng thời gian di chuyển, không có nút “Thêm vào Calendar”, không hỏi lại sở thích hay độ tuổi.

Pain thật: người dùng có gợi ý dạng chữ nhưng không thể dùng ngay, vẫn phải tự tra Maps, tự nhập Calendar, không thể điều chỉnh.

### Cụm 2 — Planning bị phân mảnh giữa nhiều tool

Người dùng phải tự nhảy qua nhiều công cụ: Google Search (tìm gợi ý), Google Maps (xem khoảng cách), blog/review (kiểm tra địa điểm), Calendar (tự tạo lịch), Messenger/Zalo (hỏi gia đình/bạn bè), Notes/Docs (lưu kế hoạch).

Pain thật: workflow bị đứt đoạn, không phải thiếu một feature nhỏ.

### Cụm 3 — AI hiện tại (ChatGPT/Gemini) mạnh ở gợi ý, yếu ở execution

Các AI chat có thể viết itinerary, nhưng nếu không kiểm chứng, không xuất lịch, không chỉnh sửa cộng tác, thì vẫn chỉ là đoạn text.

Pain thật: câu trả lời AI chưa biến thành hành động.

### Cụm 4 — User cần kiểm soát vì plan có rủi ro cá nhân

Đi chơi gia đình có trẻ nhỏ, người già, ngân sách, thời tiết và sức khỏe. Nếu AI đoán sai, hậu quả không quá nghiêm trọng như y tế/pháp lý, nhưng đủ làm người dùng mất niềm tin.

Pain thật: cần AI hỗ trợ nhưng không muốn AI tự quyết toàn bộ.

## 2. Insight

```text
User là phụ huynh hoặc nhóm bạn không chỉ cần một bản gợi ý dạng text từ Google AI Overview.
Họ thật ra cần một công cụ biến ý định mơ hồ thành lịch trình có thể dùng được,
vì evidence cho thấy Google AI Overview chỉ trả về text tĩnh, thiếu Maps, Calendar và khả năng tùy chỉnh.
```

## 3. Opportunity

```text
Cơ hội là dùng AI để augment hành động hẹp: từ yêu cầu đi chơi cuối tuần, AI hỏi thêm khi thiếu thông tin (sở thích, độ tuổi, phương tiện), tạo itinerary theo ngày/giờ, hiển thị địa điểm trên Maps, cho phép chỉnh sửa, và xuất sang Google Calendar.
Việc này giúp user giảm thời gian tìm kiếm và tổng hợp,
trong khi vẫn kiểm soát failure bằng confirmation, correction path, và yêu cầu xác minh khi thông tin chưa chắc.
```

## 4. Chọn build slice

### Build slice chính thức (đúng form)

```text
Cho phụ huynh hoặc nhóm bạn đang lên kế hoạch đi chơi cuối tuần nhưng chỉ nhận được gợi ý dạng text từ Google AI Overview,
prototype dùng AI để hỏi về sở thích, thời gian, phạm vi, phương tiện, độ tuổi,
tạo lịch trình theo khung giờ, hiển thị trên Google Maps, có nút "Thêm vào Google Calendar",
và xử lý failure mode "AI không đủ thông tin để tạo lịch" bằng cách hỏi lại các câu cụ thể (sở thích, độ tuổi, phương tiện) và đưa ra các lựa chọn gợi ý.
```

### 5 câu hỏi kiểm tra build slice

| Câu hỏi | Đánh giá |
| --- | --- |
| User cụ thể chưa? | ✅ Đạt. Phụ huynh hoặc nhóm bạn lên kế hoạch đi chơi cuối tuần. |
| Task đủ hẹp chưa? | ✅ Đạt. Chỉ build flow tạo lịch trình 1-2 ngày + Maps + xuất Calendar, không build booking thật. |
| AI decision rõ chưa? | ✅ Đạt. AI chọn/gợi ý lịch trình và thứ tự hoạt động; user quyết cuối (augmentation). |
| Failure path rõ chưa? | ✅ Đạt. AI thiếu thông tin (sở thích mơ hồ) → hỏi lại và đưa lựa chọn. |
| Có evidence không? | ✅ Đạt. Có self-use evidence (ảnh Google AI Overview) và nguồn public (TechCrunch, Stippl). Nhóm sẽ chụp ảnh xác minh các bài viết trước M1. |

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

**Quyết định:** Giữ domain Travel & Hospitality, giảm scope xuống một flow khả thi trong 1 ngày.

**Không build trong Day 06:**
- Booking thật (khách sạn, nhà hàng, vé)
- Tự động kiểm tra giá vé, giờ mở cửa, thời tiết real-time
- Collaborative editing nhiều người
- Lưu preference dài hạn
- Auto invite người thân qua Calendar
- Expense splitting
- Mobile app

**Chỉ build:**
```text
Input nhu cầu (chat hoặc form) → AI hỏi thêm nếu thiếu thông tin → tạo itinerary theo khung giờ → hiển thị địa điểm trên Maps (mock hoặc iframe) → cho phép chỉnh sửa thủ công (kéo thả hoặc sửa text) → xuất lịch dạng ICS/CSV hoặc nút "Thêm vào Google Calendar" (mock link).
```

## 6. Auto/Aug quyết định

**Chọn:** **Augmentation** (AI gợi ý, user quyết định cuối cùng).

### Lý do
AI không nên tự động quyết định lịch đi chơi vì sở thích gia đình là ngữ cảnh cá nhân, có rủi ro về thời gian, sức khỏe trẻ nhỏ. User phải giữ quyền kiểm soát và chỉnh sửa.

### Human role
- **Reviewer:** xem lại itinerary trước khi dùng.
- **Decider:** chọn giữ/bỏ địa điểm, điều chỉnh thời gian.
- **Rescuer:** sửa trực tiếp khi AI đề xuất không phù hợp.
- **Trainer:** phản hồi “không phù hợp” để cải thiện gợi ý sau.

## 7. Eval plan sơ bộ (4 paths)

| Path | Test case | Expected output |
|------|-----------|------------------|
| **Happy** | Gia đình 4 người, trẻ 7 tuổi, xuất phát Hà Nội, thích thiên nhiên, 2 ngày, ô tô. | Lịch trình 2 ngày có giờ, địa điểm, kèm Maps và nút xuất Calendar. |
| **Low‑confidence** | “Muốn đi chơi cuối tuần với gia đình” (thiếu thông tin). | AI hỏi lại: đi mấy người, có trẻ nhỏ không, từ đâu, trong ngày hay qua đêm, ngân sách. |
| **Failure** | Gia đình có trẻ 4 tuổi, yêu cầu “nhẹ nhàng, không leo núi” nhưng AI đề xuất trekking nặng. | User có nút “Không phù hợp” → AI tạo lại lịch trình nhẹ hơn. |
| **Correction** | User đổi ngày đi từ thứ 7 sang chủ nhật, bỏ một địa điểm. | AI cập nhật lại itinerary, sắp xếp lại thời gian, xuất lại lịch. |

## 8. Câu chốt cuối

```text
Dựa trên self-use evidence (Google AI Overview chỉ trả text, thiếu Maps/Calendar/tương tác), nguồn public về hạn chế của AI chat trong travel planning, và pattern từ Stippl,
nhóm sẽ build prototype “AI Weekend Planner”,
cho phụ huynh hoặc nhóm bạn đang lên kế hoạch đi chơi cuối tuần,
để giải quyết pain: Google AI Overview chỉ đưa ra gợi ý dạng text, không thể dùng ngay, không tích hợp Maps hay Calendar,
bằng cách AI augment task tạo itinerary (hỏi thêm khi thiếu thông tin, hiển thị Maps, xuất Calendar, cho phép chỉnh sửa),
và sẽ test failure path khi AI không đủ thông tin hoặc đề xuất lịch trình không phù hợp với gia đình có trẻ nhỏ.
```

## 9. Backlog (không build trong Day 06)

- Booking thật (khách sạn, nhà hàng, vé)
- Tự động kiểm tra giá vé, giờ mở cửa, thời tiết real-time
- Collaborative editing nhiều người (chia sẻ link chỉnh sửa)
- Lưu preference dài hạn (đăng nhập)
- Auto invite người thân qua Calendar
- Expense splitting
- Mobile app (chỉ web/mock)
- Maps routing real-time (chỉ hiển thị điểm, không tính đường đi thực tế nếu không đủ thời gian)
- Đồng bộ Google Calendar thật nếu không đủ thời gian (có thể thay bằng mock nút “Tạo sự kiện mẫu”)

---
