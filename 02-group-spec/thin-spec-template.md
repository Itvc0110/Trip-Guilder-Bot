# Template — Thin SPEC Cuối Day 05

Thin SPEC không phải PRD đầy đủ. Đây là bản cam kết đủ rõ để sáng Day 06 nhóm build ngay.

## 1. Track, product/app và user

**Track:** AI for Travel & Hospitality  
**Product/app thật:** Google Search (AI Overview) – dùng để lên kế hoạch đi chơi  
**User cụ thể:** Phụ huynh có con nhỏ (3–10 tuổi) hoặc nhóm bạn trẻ, đang lên kế hoạch cho một chuyến đi chơi cuối tuần tại Hà Nội.  
**Nhóm có phải user thật không? Nếu không, khác ở đâu?**  
Có. Các thành viên trong nhóm đều từng tự lên kế hoạch đi chơi cuối tuần cho gia đình/bạn bè và gặp khó khăn với việc tổng hợp thông tin từ nhiều nguồn.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|----------|-------|----------------------------|--------------------|
| Google AI Overview trả về đoạn văn bản lịch trình rất ngắn (chỉ buổi sáng), không Maps, không Calendar, không hỏi lại sở thích. | Self-use (screenshot `google-ai-overview-han-che.png`) | User chỉ nhận được gợi ý dạng text, không thể dùng ngay, phải tự tra Maps và nhập Calendar thủ công. | Tích hợp Maps và nút xuất Calendar. Thêm cơ chế hỏi lại để thu thập sở thích, độ tuổi, phương tiện. |
| *“Google đã tung thêm tính năng AI cho Search, Maps và Gemini… người dùng chuyển sang ChatGPT để lên kế hoạch chuyến đi.”* | TechCrunch (2025) | Search truyền thống không đáp ứng; người dùng cần công cụ tạo itinerary có thể chia sẻ, chỉnh sửa. | Tập trung vào khả năng chỉnh sửa, xuất lịch và cộng tác (chia sẻ để backlog). |
| *“ChatGPT tốt cho brainstorming nhưng không tạo itinerary có thể chia sẻ và chỉnh sửa cộng tác.”* | Stippl | AI text thuần chưa đủ; cần tích hợp dữ liệu thực tế và công cụ cộng tác. | Cho phép user chỉnh sửa itinerary trực tiếp (kéo thả hoặc sửa text) và lưu thay đổi. |

## 3. Pain statement

```text
User (phụ huynh hoặc nhóm bạn) đang lên kế hoạch đi chơi cuối tuần tại Hà Nội,
vì Google AI Overview chỉ trả về gợi ý dạng text tĩnh, không có bản đồ, không thể thêm vào lịch, không hỏi lại sở thích,
dẫn tới người dùng phải tự tra cứu Maps, tự nhập Calendar, mất thời gian và dễ bỏ sót.
Bằng chứng chính là ảnh chụp màn hình Google AI Overview với lịch trình chỉ vỏn vẹn vài dòng, thiếu các nút tương tác.
```

## 4. Build slice

```text
Cho phụ huynh hoặc nhóm bạn đang lên kế hoạch đi chơi cuối tuần nhưng chỉ nhận được gợi ý dạng text từ Google AI Overview,
prototype sẽ dùng AI để hỏi về sở thích, thời gian, phạm vi, phương tiện, độ tuổi,
tạo ra lịch trình theo khung giờ, hiển thị trên Google Maps (mock/iframe), kèm nút "Thêm vào Google Calendar" (mock),
và xử lý failure mode "AI không đủ thông tin để tạo lịch" bằng cách hỏi lại các câu cụ thể (sở thích, độ tuổi, phương tiện) và đưa ra các lựa chọn gợi ý.
```

## 5. Auto/Aug decision

Chọn một:

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:**  
AI không nên tự động quyết định lịch đi chơi vì sở thích gia đình là ngữ cảnh cá nhân, có rủi ro về thời gian, sức khỏe trẻ nhỏ. User phải giữ quyền kiểm soát và chỉnh sửa.

**Human role:** reviewer, decider, rescuer, trainer

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|------|------------------------------|
| Happy | User nhập đầy đủ thông tin (sở thích: công viên, thời gian: 9h-17h, phạm vi: Hà Nội, có trẻ 7 tuổi, ô tô). AI trả lịch trình 3-4 điểm kèm khung giờ, hiển thị bản đồ (mock), nút "Thêm vào Calendar". |
| Low‑confidence | User trả lời mơ hồ ("đi đâu cũng được", "thích gì cũng được"). AI hỏi lại: "Bạn thích hoạt động ngoài trời, trong nhà, hay vui chơi giải trí?" và đưa ra 3 lựa chọn để chọn. |
| Failure | AI không tìm thấy địa điểm phù hợp với sở thích (ví dụ: "công viên có chim hoàng yến"). AI thông báo: "Rất tiếc, chưa có địa điểm phù hợp. Bạn có muốn thử sở thích khác hoặc mở rộng phạm vi không?" và hiển thị gợi ý dự phòng (công viên Thống Nhất, hồ Tây, Vườn bách thú). |
| Correction | User kéo thả thứ tự địa điểm (muốn đi bảo tàng trước, công viên sau) hoặc sửa thời gian. AI tự động cập nhật lịch trình, hiển thị lại khung giờ mới và cho phép xuất Calendar. Mỗi lần chỉnh sửa được ghi log (console log) để cải thiện gợi ý sau. |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user chọn một sở thích quá đặc biệt (ví dụ: "muốn xem chim hoàng yến trong công viên") và AI không tìm thấy bất kỳ địa điểm nào phù hợp trong cơ sở dữ liệu mock,
AI có thể trả lời "Không tìm thấy" và dừng lại, khiến user bế tắc,
hậu quả là user mất niềm tin và bỏ cuộc.
Prototype sẽ xử lý bằng fallback: hiển thị 3 gợi ý phổ biến nhất cho sở thích gần nhất (ví dụ: "hoạt động ngoài trời" → gợi ý công viên Thống Nhất, hồ Tây, Vườn bách thú) và hỏi "Bạn có muốn thử các địa điểm này không?"
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

