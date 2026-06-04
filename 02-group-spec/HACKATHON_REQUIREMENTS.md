# AI IN ACTION — DAY 05

## Thiết kế sản phẩm AI cho sự bất định & Chuẩn bị Hackathon

## 1. Tư duy trung tâm của buổi học

Buổi học hôm nay chuyển trọng tâm từ việc “làm demo AI chạy được” sang việc “thiết kế một sản phẩm AI đáng tin trong bối cảnh thật”.

Một demo AI có thể chạy tốt trong môi trường sạch, với input đẹp và kỳ vọng đơn giản. Nhưng một AI Product thật phải sống trong môi trường có input bẩn, người dùng thiếu ngữ cảnh, model không chắc chắn, tool có thể lỗi, và output có thể sai. Vì vậy, thiết kế AI Product không chỉ là chọn model mạnh hay viết prompt hay. Nó là bài toán quản trị rủi ro, thiết kế fallback, xây dựng niềm tin và thu thập learning signal để sản phẩm tốt dần lên.

Thông điệp cốt lõi:
> Nếu sản phẩm dùng AI, bạn đang thiết kế cho uncertainty.

AI không giống phần mềm truyền thống. Phần mềm truyền thống thường deterministic: cùng một input thì cho cùng một output. AI thì probabilistic: output có xác suất, có sai số, có độ dao động, và có thể thay đổi theo context, model version hoặc dữ liệu đầu vào.

Do đó, AI Product không thể chỉ hỏi:
> “AI có làm được không?”

Mà phải hỏi:
> “Nếu AI không chắc thì sao?”
> “Nếu AI sai thì user phát hiện bằng cách nào?”
> “Nếu user mất niềm tin thì sản phẩm khôi phục thế nào?”
> “Nếu output sai, ai chịu trách nhiệm?”
> “Signal nào được lưu lại để hệ thống tốt hơn?”

---

# 2. AI Product bắt đầu từ Uncertainty

## 2.1 Ba lớp bất định của sản phẩm AI

AI Product có sự bất định ở ít nhất 3 lớp.

### 1. Input Uncertainty

Người dùng không luôn nhập câu hỏi rõ ràng. Họ có thể nhập thiếu thông tin, dùng ngôn ngữ mơ hồ, sai chính tả, hoặc đưa dữ liệu không đủ context.

Ví dụ:

> “Tóm tắt cái này giúp tôi.”
> “Tôi nên chọn cái nào?”
> “Có vấn đề gì không?”

Các câu này không đủ rõ nếu hệ thống không biết “cái này” là gì, tiêu chí chọn là gì, và “vấn đề” đang nói tới loại rủi ro nào.

### 2. Process Uncertainty

AI có thể gọi tool, truy vấn dữ liệu, suy luận nhiều bước, hoặc đi qua agent loop. Mỗi bước đều có khả năng lỗi:

* Tool gọi sai.
* Tool trả dữ liệu thiếu.
* Model hiểu sai output của tool.
* Agent chọn sai hành động tiếp theo.
* Prompt không đủ boundary.
* Context quá dài làm model bỏ sót thông tin.

### 3. Output Uncertainty

Output của AI không phải lúc nào cũng đúng. Nó có thể:

* Bịa thông tin.
* Đưa câu trả lời nghe hợp lý nhưng sai.
* Quá tự tin.
* Thiếu nguồn.
* Không nhất quán giữa nhiều lần chạy.
* Sai ở edge case.

Vì vậy, AI Product không nên được thiết kế như một hệ thống luôn đúng. Nó nên được thiết kế như một hệ thống biết cách xử lý khi không chắc hoặc sai.

---

## 2.2 AI Product là quản trị phân phối lỗi

Trong phần mềm truyền thống, lỗi thường được nhìn như bug cần sửa để biến mất.

Trong AI Product, lỗi không hoàn toàn biến mất. Ta phải quản trị phân phối lỗi:

* Lỗi nào có thể chấp nhận?
* Lỗi nào không thể chấp nhận?
* Lỗi nào user thấy ngay?
* Lỗi nào nguy hiểm vì user không biết?
* Khi AI sai, user có sửa được không?
* Khi AI không chắc, hệ thống có dừng lại không?

Một thiết kế AI Product tốt không hứa rằng AI luôn đúng. Nó hứa rằng khi AI sai, hệ thống vẫn có đường xử lý an toàn.

---

# 3. Error Routing: Detect → Route → Recover → Learn

Một sản phẩm AI cần có sơ đồ định tuyến lỗi.

## 3.1 Detect — Nhận biết khi hệ thống không chắc

Hệ thống cần phát hiện các dấu hiệu như:

* Confidence thấp.
* Input thiếu dữ liệu.
* User hỏi ngoài phạm vi.
* Tool failure.
* Output không có nguồn.
* Kết quả mâu thuẫn với dữ liệu.
* AI không thể phân loại rõ intent.

Nếu hệ thống không phát hiện được lúc mình không chắc, nó sẽ trả lời như thể chắc chắn. Đây là lỗi nguy hiểm.

## 3.2 Route — Chọn đường an toàn

Khi không chắc, hệ thống có thể:

* Hỏi lại người dùng.
* Escalate cho người thật.
* Chỉ đưa gợi ý thay vì tự động hành động.
* Từ chối nếu ngoài phạm vi.
* Chuyển sang workflow thủ công.
* Hiển thị cảnh báo độ tin cậy.

## 3.3 Recover — Cho phép sửa và khôi phục

Khi AI sai, user cần có cách sửa:

* Edit output.
* Undo action.
* Reject suggestion.
* Choose another option.
* Report wrong result.
* See explanation.
* Opt out.

AI Product không nên ép user chấp nhận output của AI như một quyết định cuối cùng, đặc biệt trong các tác vụ có rủi ro cao.

## 3.4 Learn — Lưu tín hiệu để cải thiện

Mỗi lần user sửa, reject, approve, retry, report hoặc handoff, đó là learning signal.

Các signal quan trọng:

* Approve rate.
* Edit distance.
* Retry rate.
* Handoff rate.
* Time-to-resolution.
* Report sai.
* Correction của user.
* Lựa chọn cuối cùng của human reviewer.

Nếu không thu signal, AI Product không tốt lên. Nó chỉ là một demo tĩnh.

---

# 4. Automation vs Augmentation

Một quyết định quan trọng trong AI Product là chọn giữa Automation và Augmentation.

## 4.1 Automation là gì?

Automation nghĩa là AI làm thay user và tự đưa hành động đến bước cuối.

Ví dụ:

* AI tự duyệt giao dịch.
* AI tự gửi email.
* AI tự đặt vé.
* AI tự phân loại và xử lý ticket.
* AI tự cập nhật hệ thống.

Automation có giá trị lớn nếu đúng, nhưng rủi ro cũng cao vì AI có quyền hành động.

## 4.2 Augmentation là gì?

Augmentation nghĩa là AI hỗ trợ user, nhưng user vẫn giữ quyền quyết định.

Ví dụ:

* AI gợi ý câu trả lời, nhân viên support duyệt.
* AI draft báo cáo, PM chỉnh sửa.
* AI đề xuất feature từ paper, sinh viên/giảng viên chọn.
* AI gợi ý route xử lý, người vận hành quyết định.

Augmentation không phải phiên bản yếu hơn của Automation. Nó là một bước chiến lược để giảm rủi ro, thu thập dữ liệu thật, học cách user ra quyết định, rồi mới tăng dần mức tự động hóa.

---

## 4.3 Agency Progression: V1 → V2 → V3

Một sản phẩm AI nên tăng mức tự động hóa theo từng giai đoạn.

### V1 — Routing / Suggestion

AI chỉ phân loại, gợi ý hoặc định tuyến.

Ví dụ:

> AI đọc ticket và gợi ý nhóm xử lý.

### V2 — Copilot

AI tạo draft hoặc đề xuất hành động, nhưng người dùng duyệt.

Ví dụ:

> AI viết nháp câu trả lời cho khách hàng, nhân viên chỉnh và gửi.

### V3 — Automation

AI tự xử lý khi đủ tin cậy, có dữ liệu và có fallback.

Ví dụ:

> AI tự xử lý ticket đơn giản, nhưng escalate case nhạy cảm.

Bài học: không nên nhảy thẳng vào V3 nếu chưa có dữ liệu thật và failure path rõ.

---

# 5. Precision vs Recall: Sai kiểu nào đắt hơn?

Khi thiết kế AI Product, không có một mức accuracy chung cho mọi sản phẩm.

Cần hỏi:

> Sai nhầm nghiêm trọng hơn hay bỏ sót nghiêm trọng hơn?

## 5.1 Precision

Ưu tiên precision khi false positive đắt.

Ví dụ:

* Gắn nhãn gian lận.
* Chẩn đoán bệnh.
* Duyệt chi phí.
* Chặn tài khoản.
* Đánh giá học sinh/sinh viên.

Nếu AI báo sai mà user không biết, rủi ro rất cao. Khi đó phải ưu tiên ít báo nhầm.

## 5.2 Recall

Ưu tiên recall khi false negative đắt.

Ví dụ:

* Cảnh báo rủi ro.
* Tìm lỗi bảo mật.
* Tìm paper liên quan.
* Gợi ý tài liệu nên đọc.

Nếu bỏ sót gây thiệt hại lớn, hệ thống nên tìm rộng hơn, nhưng cần cho user lọc lại.

## 5.3 Quy tắc thực dụng

Nếu AI sai mà user thấy ngay và sửa dễ, có thể chấp nhận recall cao hơn.

Nếu AI sai mà user không biết và hậu quả lớn, phải ưu tiên precision, human review và boundary rõ.

---

# 6. Ba trụ thiết kế AI Product: Requirement · UX · Eval

AI Product thay đổi cả 3 phần: cách viết requirement, cách thiết kế UX và cách đánh giá chất lượng.

## 6.1 Requirement: Outcome + Threshold + Fallback

Requirement của AI không nên viết kiểu:

> “AI trả lời chính xác.”

Cần viết rõ:

> “AI phải đạt outcome nào, ở ngưỡng nào, và fallback ra sao nếu không đạt.”

Công thức:

> Outcome + Threshold + Fallback

Ví dụ:

> Hệ thống gợi ý tối đa 5 paper liên quan cho problem statement của sinh viên. Ít nhất 4/5 paper phải được reviewer đánh giá là liên quan. Nếu confidence thấp, hệ thống phải yêu cầu sinh viên bổ sung keyword hoặc topic context.

Requirement tốt phải chỉ ra:

* Output mong muốn.
* Ngưỡng chấp nhận.
* Điều kiện không chắc.
* Cơ chế fallback.
* Ai kiểm tra.
* Metric đo.

---

## 6.2 UX: Thiết kế cho lúc AI sai

AI UX không chỉ là màn hình đẹp. AI UX là cách sản phẩm xử lý khi AI đúng, không chắc, sai, hoặc làm user mất tin.

4 paths UX cho mỗi AI feature:

### Path 1 — Khi AI đúng

Câu hỏi:

> Value moment là gì?

User phải thấy rõ giá trị ngay khi AI làm đúng.

Ví dụ:

> AI gợi ý đúng 5 paper liên quan và giải thích vì sao nên đọc.

### Path 2 — Khi AI low-confidence

Câu hỏi:

> AI làm gì khi không chắc?

Có thể:

* Hỏi thêm.
* Hiển thị confidence.
* Đề xuất lựa chọn.
* Escalate.
* Không tự động hành động.

### Path 3 — Khi AI sai

Câu hỏi:

> User sửa lỗi bằng cách nào?

Cần có:

* Edit.
* Reject.
* Undo.
* Report.
* Compare with source.
* Choose alternative.

### Path 4 — Khi user mất tin

Câu hỏi:

> Làm sao khôi phục trust?

Cần có:

* Explanation.
* Source citation.
* Opt-out.
* Manual mode.
* Human review.
* Audit trail.

---

## 6.3 Eval: Đánh giá phân phối chất lượng

Eval của AI không giống test phần mềm truyền thống.

Phần mềm truyền thống thường pass/fail. AI thì chất lượng nằm trên spectrum.

Không nên chỉ nói:

> “Model đạt 87% accuracy.”

Cần hỏi:

> 13% sai nằm ở đâu?
> Sai ở case nào?
> Sai có nguy hiểm không?
> Sai có sửa được không?
> User có phát hiện được không?

Ở giai đoạn đầu, qualitative evaluation thường quan trọng hơn quantitative evaluation. Hãy xem từng output, phân loại lỗi, rồi mới viết eval.

Một cách bắt đầu:

1. Lấy 50–100 outputs.
2. Đọc thủ công.
3. Nhóm lỗi thành pattern.
4. Viết eval từ error patterns.
5. Đo lại sau khi sửa prompt/model/workflow.

---

# 7. Graceful Failure & Trust Recovery

Một sản phẩm AI tốt không phải là sản phẩm không bao giờ sai. Đó là sản phẩm sai một cách có kiểm soát.

## 7.1 Graceful Failure

Graceful Failure nghĩa là khi AI sai hoặc không chắc, sản phẩm vẫn không “gãy”.

Ví dụ tốt:

> “Tôi chưa đủ dữ liệu để kết luận. Bạn có thể upload thêm paper hoặc chọn một trong ba hướng sau.”

Ví dụ xấu:

> AI bịa câu trả lời nghe chắc chắn.

## 7.2 Trust Recovery

Trust Recovery nghĩa là khi user nghi ngờ hoặc phát hiện AI sai, sản phẩm có cách khôi phục niềm tin.

Cách làm:

* Hiển thị nguồn.
* Cho sửa.
* Cho phản hồi.
* Cho xem reasoning vừa đủ.
* Cho quay về manual mode.
* Cho human review.
* Không giấu uncertainty.

Người dùng có thể chấp nhận AI không hoàn hảo nếu chi phí sửa thấp và họ vẫn giữ quyền kiểm soát.

---

# 8. AI Product Canvas

AI Product Canvas giúp gom Requirement, UX và Eval vào một artifact.

Có thể nhìn theo 3 cột chính:

## 8.1 Value

Sản phẩm tạo giá trị gì?

Cần trả lời:

* User là ai?
* Pain là gì?
* Task cụ thể là gì?
* Outcome mong muốn là gì?
* AI giúp ở bước nào?
* Nếu không có AI thì user làm thế nào?

## 8.2 Trust

Làm sao user tin và kiểm soát được AI?

Cần trả lời:

* AI có thể sai ở đâu?
* User phát hiện lỗi thế nào?
* Có source/citation không?
* Có human review không?
* Có undo/edit/reject không?
* Có fallback không?

## 8.3 Feasibility

Có build được không?

Cần trả lời:

* Dữ liệu có sẵn không?
* Tool/API có sẵn không?
* Scope có đủ nhỏ không?
* Eval đo được không?
* Có prototype được trong thời gian ngắn không?
* Chi phí chạy có hợp lý không?

## 8.4 Learning Signal Row

AI Product không chỉ cần output. Nó cần signal để học.

Cần trả lời:

* User sửa gì?
* User reject gì?
* User chọn option nào?
* User retry bao nhiêu lần?
* Case nào cần human handoff?
* Những correction này được lưu ở đâu?

---

# 9. Feedback Loop & Data Flywheel

AI Product là organism, không phải artifact.

Một sản phẩm phần mềm truyền thống có thể build xong rồi release. Nhưng AI Product cần vòng lặp học liên tục.

## 9.1 Feedback Loop

Loop cơ bản:

> Ingest → Digest → Output → Repeat

* Ingest: nhận input, dữ liệu, hành vi user.
* Digest: model xử lý, phân tích, suy luận.
* Output: trả kết quả cho user.
* Repeat: user sửa, approve, reject, hệ thống học lại.

KPI mới của AI Product không chỉ là feature usage, mà là tốc độ và chất lượng của feedback loop.

## 9.2 Data Flywheel

Data flywheel:

> Có user → thu dữ liệu thật → AI tốt hơn → user tin hơn → có thêm user → thu thêm dữ liệu

Khi model capability ngày càng commodity hóa, lợi thế thật không nằm ở việc “dùng model nào”, mà nằm ở dữ liệu riêng:

* Domain data.
* User-specific data.
* Human judgment.
* Correction data.
* Workflow data.

---

# 10. Case Studies quan trọng

## 10.1 GitHub Copilot

GitHub Copilot không cần accuracy tuyệt đối để tạo giá trị. Nếu gợi ý sai, developer chỉ cần bỏ qua hoặc tiếp tục gõ. Cost of reject gần như bằng 0.

Bài học:

> Augmentation có thể thành công ngay cả khi accuracy chưa hoàn hảo, nếu UX làm cho việc từ chối/sửa lỗi cực rẻ.

## 10.2 Harvey Legal AI

Trong legal domain, AI sai có thể gây hậu quả lớn. Vì vậy Harvey phải ưu tiên precision, đầu tư vào accuracy, và có thể bán với giá cao vì value và risk đều cao.

Bài học:

> Domain càng rủi ro, càng cần boundary, eval và human review mạnh.

## 10.3 Microsoft Tay

Tay thất bại vì không có failure design và moderation đủ tốt. Bot bị troll và tạo output độc hại.

Bài học:

> Không có graceful failure và content boundary thì chatbot có thể bị bẻ lái rất nhanh.

## 10.4 Customer Support Agent V1 → V3

Một số team nhảy thẳng vào agent tự xử lý toàn bộ ticket và phải shutdown vì lỗi quá nhiều. Hướng tốt hơn là:

* V1: routing.
* V2: draft copilot.
* V3: automation sau khi có data.

Bài học:

> Bắt đầu bằng augmentation, tăng dần automation khi có evidence.

## 10.5 Microsoft Dragon

Dragon cải thiện mạnh nhờ dữ liệu thật và chuyên gia đánh giá. Synthetic data ban đầu không đủ. Dữ liệu thật + human evaluation mới tạo ra improvement rõ.

Bài học:

> Feedback loop và dữ liệu domain thật là lợi thế cạnh tranh của AI Product.

---

# 11. Find → Synthesize → Decide

Quy trình nghiên cứu và ra quyết định trong AI Product có thể tóm thành:

> Find → Synthesize → Decide

## 11.1 Find — Tìm bằng chứng

Không bắt đầu bằng “ý tưởng hay”. Bắt đầu bằng evidence.

Nguồn evidence nhanh:

* Tự trải nghiệm sản phẩm.
* Phỏng vấn user thật.
* Quan sát workflow.
* Review mining trên App Store, Google Play, Reddit, Facebook group.
* Screenshot lỗi.
* Quote từ user.
* Log/ticket nếu có.

Evidence tốt phải chỉ ra:

* Ai đau?
* Đau ở đâu?
* Đau thường xuyên không?
* Hậu quả là gì?
* Hiện tại user workaround thế nào?

## 11.2 Synthesize — Tổng hợp thành insight

Không chỉ copy quote. Phải chuyển quote thành quyết định.

Ví dụ:

Quote:

> “App cứ gợi ý sai địa điểm nên tôi phải tự search lại.”

Insight:

> User không cần AI tự quyết địa điểm. Họ cần AI đề xuất nhưng phải cho sửa nhanh và hiển thị lý do gợi ý.

Decision:

> Chọn augmentation thay vì automation. Build editable plan thay vì auto-booking.

## 11.3 Decide — Chọn lát cắt build

Đừng build toàn bộ app. Chọn một build slice:

* Một user.
* Một task.
* Một AI decision.
* Một output.
* Một failure path.

Nếu lát cắt quá rộng, prototype sẽ đẹp nhưng không chứng minh được product thinking.

---

# 12. Thin SPEC

Thin SPEC là bản đặc tả mỏng để nhóm có thể build nhanh nhưng vẫn đúng trọng tâm.

Thin SPEC nên có 5 phần.

## 12.1 Evidence

Bằng chứng pain thật:

* Screenshot.
* Review.
* Quote.
* Interview.
* Observation.
* Log.
* Survey nhỏ.

Cần ghi rõ evidence đến từ đâu và nó chứng minh điều gì.

## 12.2 Build Slice

Lát cắt build:

> Một user, một task, một AI decision, một output.

Ví dụ:

> Sinh viên mới nghiên cứu upload một problem statement và 5 paper. AI gợi ý 3 feature khả thi từ các paper đó. Sinh viên chọn hoặc reject từng feature.

## 12.3 Auto/Aug

Quyết định AI là automation hay augmentation.

Cần ghi rõ:

* AI gợi ý hay tự làm?
* Human giữ quyền ở đâu?
* Ai review output?
* Output nào không được tự động chốt?

## 12.4 Four Paths

Thiết kế 4 đường đi:

1. AI đúng → user nhận value.
2. AI low-confidence → hỏi thêm/escalate.
3. AI sai → user sửa/reject.
4. User mất tin → explain/source/opt-out/manual mode.

## 12.5 Owner Plan

Ai làm gì?

* Research.
* SPEC.
* Prototype.
* Test.
* Demo.
* Repo.
* Slide.
* Reflection.

Nếu thiếu owner plan, nhóm sẽ mất thời gian vào ngày build.

---

# 13. Vibe Coding có kiểm soát

Vibe coding không có nghĩa là để AI builder nghĩ hộ product.

Vibe coding đúng nghĩa là:

> Dùng AI builder để biến SPEC đã rõ thành prototype có bằng chứng.

Không nên prompt:

> “Làm cho tôi một app AI đẹp.”

Nên prompt:

> “Dựng flow input → AI output → human review → fallback. App cần chứng minh một happy path và một failure path.”

Quy trình vibe coding có kiểm soát:

1. SPEC — Chốt lát cắt.
2. BUILD — Dựng đúng flow.
3. TEST — Chạy happy case và failure case.
4. EVIDENCE — Lưu screenshot, prompt/log, test case, tradeoff.

Prototype không cần full app. Nhưng phải chứng minh được:

* AI decision là gì.
* User nhận value ở đâu.
* AI sai thì sao.
* Human giữ quyền ở đâu.

---

# 14. Thông tin Hackathon

## 14.1 Hackathon này là gì?

Hackathon là giai đoạn nhóm chuyển từ học framework sang làm sản phẩm AI thực tế.

Mục tiêu không phải build app hoàn chỉnh. Mục tiêu là chứng minh nhóm hiểu:

* User pain thật.
* Evidence thật.
* Build slice đủ nhỏ.
* AI augment hay automate.
* Failure path.
* Prototype chứng minh AI behavior.
* Demo narrative rõ.

## 14.2 Track là gì?

Track là một miền app thật để soi và cải tiến.

Các track gồm:

* Learning OS.
* Travel.
* Food Delivery.
* Finance.
* Healthcare.

Track không phải scope. Mỗi nhóm phải cắt track thành một flow nhỏ.

Ví dụ:

Không nên làm:

> “AI cho Food Delivery.”

Nên làm:

> “AI giúp user chọn món trưa khi có constraint về ngân sách, khẩu vị và thời gian giao, nhưng vẫn cho user sửa plan khi AI gợi ý sai.”

---

## 14.3 Nhóm cần làm gì?

Quy trình tổng thể:

> Research → Thin SPEC → Prototype → Test → Demo

Nhóm cần:

1. Tìm evidence thật.
2. Chọn một pain.
3. Cắt một build slice.
4. Quyết định augment hay automate.
5. Thiết kế 4 paths.
6. Build prototype.
7. Test happy case và failure/low-confidence case.
8. Chuẩn bị demo narrative.
9. Nộp repo cá nhân.

---

# 15. Nhiệm vụ tối Day 05

Tối Day 05 chưa cần build xong. Nhưng phải chốt 5 yếu tố.

## 15.1 Evidence — User + pain thật

Cần có ít nhất một loại evidence:

* Screenshot.
* Review.
* Quote.
* Observation.
* Interview nhanh.
* App behavior.
* User complaint.

Không có evidence thì pain vẫn chỉ là giả định.

## 15.2 Slice — Một flow đủ nhỏ

Một flow tốt gồm:

* Một user.
* Một task.
* Một AI decision.
* Một output.

Không được chọn scope quá rộng.

## 15.3 Decision — Augment hay Automate?

Cần trả lời:

* AI gợi ý hay tự làm?
* Human giữ quyền ở đâu?
* Khi nào AI phải dừng?
* AI sai thì ai sửa?

## 15.4 Failure — Path phải test

Cần có ít nhất:

* 1 happy case.
* 1 low-confidence hoặc failure case.

Nếu prototype không chứng minh failure path, demo đẹp vẫn chưa đủ.

## 15.5 Owner — Ai làm gì sáng mai?

Cần phân công:

* Ai research?
* Ai viết SPEC?
* Ai build prototype?
* Ai test?
* Ai chuẩn bị demo?
* Ai quản lý repo?
* Ai làm reflection?

Nếu thiếu 5 thứ này, Day 06 sẽ mất nhiều thời gian để chọn lại hoặc sửa hướng.

---

# 16. Day 06

Day 06 tập trung vào:

* Build.
* Test.
* Dry run.
* Hoàn thiện demo.
* Chuẩn bị repo.

Nhóm cần có prototype nhìn được flow, test được ít nhất hai case, và kể được câu chuyện sản phẩm.

Không cần full app. Cần chứng minh tư duy sản phẩm.

---

# 17. Prototype có 3 mức

## Level 1 — Sketch

Đủ nếu:

* Flow rõ tất cả bước.
* Có prompt/test minh họa AI behavior.
* Tất cả thành viên giải thích được.

Phù hợp nếu không kịp code nhưng vẫn chứng minh product thinking.

## Level 2 — Mock Prototype

Có thể là:

* HTML.
* App mock.
* Figma.
* Demo UI giả lập.

Cần thể hiện:

* Output AI.
* Fallback.
* Edge case.
* User flow rõ.

## Level 3 — Working Prototype

Có input → AI → output thật.

Cần:

* Demo live được.
* Chạy ổn.
* Narrative rõ.
* Có happy path và failure path.

Điểm quan trọng:

> Prototype không cần full app, nhưng phải chứng minh được một AI decision và một path khi AI không chắc hoặc sai.

---

# 18. Submission Gate

Mỗi học viên cần nộp một repo cá nhân public.

Repo nên tách rõ:

## group/

Chứa phần nhóm:

* SPEC final.
* README.
* Slide.
* Prompt log.
* Failure log.
* Demo evidence.
* Prototype files nếu có.

## individual/

Chứa phần cá nhân:

* Reflection.
* Vai trò của cá nhân.
* Đóng góp.
* Học được gì.
* AI đã hỗ trợ gì.
* AI sai ở đâu.
* Nếu làm lại sẽ đổi gì.

---

# 19. Cách demo tốt

Một demo tốt không bắt đầu bằng feature. Nó bắt đầu bằng pain và evidence.

Flow demo nên là:

1. User là ai?
2. Pain thật là gì?
3. Evidence lấy từ đâu?
4. Build slice là gì?
5. AI decision là gì?
6. Vì sao chọn augment/automate?
7. Happy path chạy thế nào?
8. Failure/low-confidence path xử lý ra sao?
9. Human giữ quyền ở đâu?
10. Learning signal nào được thu?
11. Next step sau hackathon là gì?

Câu hỏi tự kiểm:

* Nếu AI đúng, user nhận value ở đâu?
* Nếu AI không chắc, hệ thống làm gì?
* Nếu AI sai, user sửa thế nào?
* Nếu user mất tin, sản phẩm khôi phục trust ra sao?
* Prototype có chứng minh được điều đó không?

---

# 20. Tóm tắt bằng MindSeeds

## Problem first. AI second.

Đừng bắt đầu từ model hay demo. Bắt đầu từ pain thật, user thật, evidence thật.

## Uncertainty is the product surface.

Nếu dùng AI, phần không chắc không phải ngoại lệ. Nó là thứ sản phẩm phải thiết kế.

## Augmentation is not failure.

AI hỗ trợ con người ra quyết định là một chiến lược đúng, không phải phiên bản yếu hơn automation.

## Failure path proves product thinking.

Prototype đẹp nhưng không có failure path thì chưa chứng minh được AI Product.

## Evidence earns investment.

Ý tưởng không được đầu tư vì nghe hay. Nó cần evidence, SPEC, test case và failure handling.

## The loop is the product.

AI Product tốt lên nhờ user correction, feedback, signal và human judgment.

## UX is risk management.

AI UX không chỉ là giao diện đẹp. Nó là cách user kiểm soát, sửa lỗi và lấy lại niềm tin.

---

# 21. Checklist cuối trước Hackathon

## Evidence

* [x] Có screenshot/review/quote/interview/observation.
* [x] Evidence chứng minh pain thật.
* [x] Biết user cụ thể là ai.

## Thin SPEC

* [ ] Một user.
* [ ] Một task.
* [ ] Một AI decision.
* [ ] Một output.
* [ ] Một failure path.

## Auto/Aug

* [ ] Biết AI gợi ý hay tự làm.
* [ ] Biết human giữ quyền ở đâu.
* [ ] Biết khi nào AI phải dừng.

## UX Paths

* [ ] Happy path.
* [ ] Low-confidence path.
* [ ] Wrong-output correction path.
* [ ] Trust recovery path.

## Prototype

* [ ] Có flow nhìn được.
* [ ] Có AI behavior.
* [ ] Có fallback.
* [ ] Có ít nhất 2 test case.

## Demo

* [ ] Pitch pain trước feature.
* [ ] Có evidence.
* [ ] Có prototype.
* [ ] Có failure handling.
* [ ] Có reflection.

## Repo

* [ ] Repo public.
* [ ] Có group/.
* [ ] Có individual/.
* [ ] Có README.
* [ ] Có SPEC.
* [ ] Có prompt/failure log.
* [ ] Có reflection cá nhân.

---

# 22. Kết luận cuối

Bài học hôm nay không chỉ dạy cách làm sản phẩm AI. Nó dạy cách nghĩ khác khi sản phẩm có xác suất, sai số và sự bất định.

Một AI Product tốt không phải là sản phẩm có model mạnh nhất. Nó là sản phẩm biết:

* bắt đầu từ pain thật,
* chọn đúng mức automation,
* thiết kế cho lúc AI sai,
* đo chất lượng bằng eval phù hợp,
* giữ người dùng trong vòng kiểm soát,
* và thu learning signal để sản phẩm tốt dần lên.

Trong Hackathon, mục tiêu không phải làm app lớn. Mục tiêu là chứng minh một lát cắt nhỏ nhưng đúng:

> Một user thật, một pain thật, một AI decision rõ, một happy path, một failure path, và một demo cho thấy nhóm hiểu cách thiết kế sản phẩm AI trong thế giới không chắc chắn.
