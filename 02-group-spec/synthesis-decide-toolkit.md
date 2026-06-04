# Synthesis & Decide — Từ Evidence đến Build Slice (Cặp Đôi Hẹn Hò)

## 1. Gom evidence thành cụm

Không gom theo feature, gom theo workflow/pain.

### Cụm 1 — Google AI Overview chỉ trả text, thiếu tương tác & tích hợp
Self-use evidence cho thấy Google AI Overview trả về đoạn văn bản lịch trình rất ngắn (chỉ buổi sáng), không có nút tương tác, không hiển thị bản đồ, không ước lượng thời gian di chuyển, không có nút “Thêm vào Calendar”, không hỏi lại sở thích hay vibe buổi hẹn hò.
*Pain thật:* Người dùng có gợi ý hẹn hò dạng chữ nhưng không thể dùng ngay, vẫn phải tự tra Maps, tự nhập Calendar, không thể điều chỉnh hành trình.

### Cụm 2 — Planning bị phân mảnh giữa nhiều tool
Người dùng phải tự nhảy qua nhiều công cụ: Google Search (tìm gợi ý lãng mạn), Google Maps (xem khoảng cách, đường đi), Facebook/Tiktok/blog/review (kiểm tra không gian, đồ ăn), Calendar (tự tạo lịch), Messenger/Zalo (bàn bạc với người yêu), Notes/Docs (lưu kế hoạch).
*Pain thật:* Workflow lập kế hoạch hẹn hò bị đứt đoạn, dễ gây bất đồng ý kiến hoặc mất kiên nhẫn.

### Cụm 3 — AI hiện tại (ChatGPT/Gemini) mạnh ở gợi ý, yếu ở execution
Các AI chat có thể viết itinerary hẹn hò rất bay bổng, nhưng nếu không kiểm chứng (địa điểm còn mở cửa không, có đông không), không xuất lịch, không hiển thị bản đồ trực quan thì vẫn chỉ là đoạn text tĩnh.
*Pain thật:* Câu trả lời AI chưa biến thành hành động thực tế.

### Cụm 4 — User cần kiểm soát vì hẹn hò có rủi ro phá hỏng trải nghiệm cảm xúc
Buổi hẹn hò của cặp đôi rất nhạy cảm với các yếu tố như: không gian quá ồn ào/không đúng vibe, quán quá đông phải xếp hàng chờ đợi lâu, hoặc di chuyển quá xa gây mệt mỏi. Nếu AI đề xuất sai không gian, buổi hẹn hò có thể bị hỏng hoàn toàn.
*Pain thật:* Cặp đôi cần AI hỗ trợ gợi ý nhanh nhưng phải nắm quyền kiểm soát để tinh chỉnh không gian và thời gian theo ý muốn, đặc biệt cần biết trước lượng người đi để tránh quá tải.

---

## 2. Insight

```text
User là các cặp đôi tại Hà Nội không chỉ cần một bản gợi ý địa điểm hẹn hò dạng text từ Google AI Overview.
Họ thật ra cần một công cụ biến ý định hẹn hò mơ hồ thành một lịch trình trải nghiệm mượt mà, lãng mạn và không bị chen chúc,
vì evidence cho thấy Google AI Overview chỉ trả về text tĩnh, thiếu Maps, Calendar và khả năng kiểm soát độ đông đúc hay vibe địa điểm.
```

---

## 3. Opportunity

```text
Cơ hội là sử dụng AI Agent để augment hành động hẹn hò cuối tuần: từ yêu cầu của cặp đôi, AI làm rõ vibe mong muốn (riêng tư, ẩm thực, năng động), thời gian và khu vực; tự động tạo itinerary theo giờ; hiển thị lượng người dự kiến lập kế hoạch đi cùng thời điểm; hiển thị các điểm trên bản đồ trực quan; cho phép kéo thả chỉnh sửa/thay thế; và xuất sang Google Calendar.
Việc này giúp các cặp đôi tạo kế hoạch hẹn hò hoàn hảo chỉ trong 1 phút, giảm thiểu rủi ro chen chúc hoặc đi nhầm quán không hợp vibe,
trong khi vẫn kiểm soát rủi ro bằng UI kéo thả thủ công và danh sách gợi ý dự phòng (fallback).
```

---

## 4. Chọn build slice

### Build slice chính thức (đúng form)

```text
Cho các cặp đôi ở Hà Nội đang lên kế hoạch hẹn hò cuối tuần nhưng chỉ nhận được gợi ý dạng text từ Google AI Overview,
prototype sử dụng ReAct Agent (DeepSeek-v4-flash) kết hợp 4 công cụ (New Experience, Favourable Place, Current Trend, Map & Export) để làm rõ sở thích vibe, gợi ý lịch trình hẹn hò chi tiết theo khung giờ, hiển thị lượng người dự kiến đi để tránh quá tải, hiển thị bản đồ trực quan, hỗ trợ kéo thả chỉnh sửa và xuất lịch sang Google Calendar (.ics).
```

### 5 câu hỏi kiểm tra build slice

| Câu hỏi | Đánh giá |
| --- | --- |
| User cụ thể chưa? | ✅ Đạt. Cặp đôi hẹn hò hoặc đã kết hôn tại Hà Nội (không dắt con nhỏ). |
| Task đủ hẹp chưa? | ✅ Đạt. Chỉ build flow tạo lịch trình hẹn hò trong ngày/cuối tuần + Maps + xuất Calendar + kiểm tra độ đông đúc. Không làm booking thật. |
| AI decision rõ chưa? | ✅ Đạt. AI Agent gợi ý lịch trình và dùng công cụ lọc địa điểm; user review và tự tay điều chỉnh (augmentation). |
| Failure path rõ chưa? | ✅ Đạt. AI thiếu thông tin vibe hoặc gặp yêu cầu quá dị biệt → kích hoạt UI hỏi lại hoặc gợi ý các địa điểm lãng mạn dự phòng. |
| Có evidence không? | ✅ Đạt. Có self-use evidence từ Google AI Overview thiếu tính năng tương tác hẹn hò và các nguồn review về pain point của travel planner hiện tại. |

---

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

**Quyết định:** Giữ nguyên domain Travel & Hospitality, tập trung vào đối tượng Cặp đôi hẹn hò.

**Không build trong Day 06 (Backlog):**
- Đặt chỗ/booking thật (bàn ăn, vé phim, phòng khách sạn).
- Hệ thống đề xuất máy học (ML Recommendation system) phức tạp.
- So sánh giá vé, tích hợp thời tiết real-time.
- Chỉnh sửa cộng tác thời gian thực giữa 2 thiết bị (collaborative editing).
- Đồng bộ tự động 2 chiều với Google Calendar API (chỉ làm nút tải file `.ics` hoặc link tạo event mẫu).

**Chỉ build:**
```text
Giao diện Chat kết hợp Bản đồ → Chọn/Nhập yêu cầu hẹn hò → ReAct Agent phân tích và hỏi lại vibe nếu thiếu thông tin → Tạo itinerary hẹn hò theo giờ kèm chỉ số lượng người dự kiến để tránh quá đông → Hiển thị điểm hẹn hò trên bản đồ (Leaflet JS/Google Maps iframe) → Cho phép chỉnh sửa (kéo thả hoặc thay thế) → Xuất lịch hẹn hò (.ics) → In JSON log sự kiện ra console.
```

---

## 6. Auto/Aug quyết định

**Chọn:** **Augmentation** (AI gợi ý lịch hẹn hò, user quyết định cuối cùng).

### Lý do
Không gian hẹn hò mang tính riêng tư và cảm xúc cao. AI không thể cảm nhận thay con người xem quán cafe đó có thực sự "hợp mắt" hay không. Việc để user tự do review, kéo thả và thay đổi địa điểm giúp tăng sự tin tưởng và tính khả thi của lịch trình.

### Human role
- **Reviewer:** Xem lại vibe địa điểm, lượng người dự kiến có quá đông không.
- **Decider:** Chấp nhận lịch trình hoặc bấm nút đổi địa điểm khác cùng vibe.
- **Rescuer:** Kéo thả đổi giờ, tự do chỉnh sửa timeline.
- **Trainer:** Phản hồi thông qua các hành động chỉnh sửa để hệ thống ghi log cải thiện seed database.

---

## 7. Eval plan sơ bộ (4 paths)

| Path | Test case | Expected output |
|------|-----------|------------------|
| **Happy** | Cặp đôi 2 người, vibe lãng mạn riêng tư, đi chiều tối thứ 7, xe máy, xuất phát Hoàn Kiếm. | Lịch trình 3 điểm (cafe ngắm hoàng hôn hồ Tây, dinner lãng mạn phố cổ, quán pub nhỏ ẩn mình) kèm giờ giấc cụ thể, hiển thị lượng người dự kiến, bản đồ và nút xuất Calendar hoạt động. |
| **Low‑confidence** | Nhập mơ hồ: "đi chơi cuối tuần đi em". | AI Agent không đoán bừa mà hiển thị Clarification UI với 3 nút lựa chọn vibe hẹn hò: *(1) Lãng mạn & Riêng tư, (2) Năng động & Trải nghiệm mới, (3) Ẩm thực & Phố xá*. |
| **Failure** | Nhập yêu cầu bất khả thi: "quán cafe phục vụ nước ép sao hỏa tại Hà Nội". | AI phản hồi lịch sự không tìm thấy địa điểm phù hợp, kích hoạt fallback hiển thị 3 địa điểm hẹn hò lãng mạn dự phòng kinh điển (Hồ Tây, Cầu Long Biên, Cafe Yên) kèm câu hỏi gợi ý. |
| **Correction** | User kéo thả dời lịch ăn tối lên trước lịch đi cafe, hoặc xóa điểm dạo phố cổ. | Timeline tự động cập nhật lại khung giờ di chuyển và hoạt động; bản đồ cập nhật marker thứ tự; console in ra JSON log của sự kiện chỉnh sửa. |

---

## 8. Câu chốt cuối

```text
Dựa trên self-use evidence (Google AI Overview chỉ trả text tĩnh, thiếu tích hợp tương tác/Maps/Calendar cho cặp đôi) và đặc thù nhạy cảm của các buổi hẹn hò tại Hà Nội (ngại đông đúc, cần hợp vibe lãng mạn),
nhóm sẽ build prototype “Trip-Guilder-Bot” (AI Weekend Planner dành cho Cặp đôi),
giúp các cặp đôi lên lịch hẹn hò chỉ trong vài giây,
bằng cách sử dụng ReAct Agent (DeepSeek-v4-flash) kết hợp 4 công cụ (New Experience, Favourable Place, Current Trend, Map & Export) để gợi ý lịch trình, kiểm soát lượng người để tránh đông đúc, hiển thị trên bản đồ, hỗ trợ kéo thả chỉnh sửa và xuất Calendar,
đồng thời xử lý các trường hợp low-confidence (hỏi lại vibe) hoặc failure (fallback điểm hẹn hò lãng mạn kinh điển).
```
