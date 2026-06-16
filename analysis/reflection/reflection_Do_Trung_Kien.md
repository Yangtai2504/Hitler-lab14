# Individual Reflection — Đỗ Trung Kiên (2A202600711)

**Phụ trách:** Multi-Judge Consensus Engine (AI/Backend team) + Tối ưu Chi phí Eval
**Module chính:** `engine/llm_judge.py`, `engine/vertex_client.py`, `analysis/cost_optimization_experiment.py`, `analysis/cost_optimization.md`

## 1. Engineering Contribution

- Viết `engine/vertex_client.py`: client dùng chung gọi Gemini qua Vertex AI (`google.genai`, mode `vertexai=True`), chạy hàm sync của SDK trong `asyncio.to_thread` để không block event loop khi nhiều request chạy song song. Module này tính cả `usage_metadata` (input/output token) và cost theo bảng giá tham khảo `PRICING_PER_1K_TOKENS` cho từng model.
- Thêm cơ chế retry với exponential backoff (`time.sleep(2 ** attempt)`, tối đa 5 lần) khi gặp lỗi `429 RESOURCE_EXHAUSTED` từ Vertex — cần thiết vì pipeline gọi rất nhiều request đồng thời và dễ bị rate-limit.
- Triển khai `LLMJudge.evaluate_multi_judge()` trong `engine/llm_judge.py`: gọi **2 model Judge khác nhau thật** (`gemini-2.5-flash` và `gemini-2.5-pro`, cấu hình qua `.env`), mỗi model chấm điểm 1–5 theo rubric Accuracy + Tone, trả JSON `{"score": ..., "reasoning": ...}`.
- Logic xử lý xung đột: nếu 2 Judge lệch điểm > 1, hệ thống tự động gọi thêm model thứ 3 (`gemini-2.5-flash-lite`) làm tie-breaker và lấy median của 3 điểm; nếu lệch ≤ 1, lấy trung bình của 2 điểm.
- Kết quả thật trên 60 case: **Agreement Rate = 92.5%**, chỉ 1/60 case phải dùng tie-breaker (ghi trong `reports/summary.json`).
- Phân tích cost breakdown thật từ `reports/benchmark_results.json`: phần Judge chiếm **75.6%** tổng chi phí eval (0.0495/0.0655 USD), do luôn gọi cả Gemini Pro (đắt ~4x input, ~2x output so với Flash) cho mọi case kể cả case dễ.
- Triển khai `LLMJudge.evaluate_multi_judge_cascade()`: gọi Flash trước, chỉ escalate sang Pro khi điểm Flash rơi vào vùng không chắc chắn (2–4/5); giữ nguyên `evaluate_multi_judge()` (luôn 2 model) làm mặc định cho benchmark chính thức để không vi phạm yêu cầu rubric về tối thiểu 2 Judge.
- Viết `analysis/cost_optimization_experiment.py` đo lại Cascade Judge trên đúng 60 cặp Q&A thật đã có (không gọi lại Agent, chỉ đo riêng phần Judge để so sánh công bằng). Kết quả thật (`analysis/cost_optimization_result.json`): **giảm 54.1% chi phí Judge**, avg_score không giảm mà tăng nhẹ (4.358 → 4.383), chỉ 13/60 case (21.7%) cần escalate sang Pro — vượt mục tiêu 30% đề ra trong README.

## 2. Technical Depth

- **Agreement Rate (Calibration) trong implementation hiện tại:** được tính theo độ lệch tuyệt đối giữa 2 điểm Judge — lệch 0 → agreement 1.0, lệch 1 → agreement 0.5, lệch > 1 → agreement 0.0. Đây là cách đo đơn giản, dễ diễn giải khi giao tiếp với stakeholder không chuyên thống kê.
- **Cohen's Kappa (khái niệm, chưa triển khai trong code):** là chỉ số đo độ đồng thuận giữa 2 "rater" có hiệu chỉnh theo xác suất đồng thuận ngẫu nhiên — công thức `κ = (p_o − p_e) / (1 − p_e)`, trong đó `p_o` là tỉ lệ đồng thuận quan sát được, `p_e` là tỉ lệ đồng thuận kỳ vọng nếu chấm ngẫu nhiên. Khác với Agreement Rate đơn giản (chỉ đếm % khớp), Cohen's Kappa quan trọng hơn khi thang điểm có nhiều mức (1–5) vì 2 Judge có thể "ngẫu nhiên trùng điểm" khá thường xuyên nếu phần lớn câu trả lời đều dễ (điểm cao) — Kappa giúp tránh đánh giá quá lạc quan về độ tin cậy của hệ thống Judge.
- **Position Bias:** thiên vị do thứ tự xuất hiện của 2 câu trả lời khi so sánh A/B (model có xu hướng ưu tiên câu trả lời đứng trước/sau). Hàm `check_position_bias()` đã được khai báo trong `llm_judge.py` làm placeholder cho hướng mở rộng (so sánh response của 2 phiên bản Agent, đổi chỗ A/B để kiểm tra Judge có nhất quán không) nhưng **chưa được triển khai logic thật** trong phạm vi lab này — đây là một hạn chế cần ghi nhận trung thực, không phải đã làm.
- **Trade-off Cost vs Quality:** dùng 2 model full-size (Flash + Pro) cho mọi case tốn chi phí hơn so với chỉ dùng 1 model, nhưng đổi lại tăng độ tin cậy (giảm rủi ro 1 model judge sai lệch một mình). Chi phí trung bình đo được: ~0.0011 USD/case (bao gồm cả generation + judge), khá rẻ vì hầu hết case chỉ cần 2 lần gọi judge.
- **Vì sao Cascade không làm giảm độ tin cậy:** dữ liệu thật cho thấy 85% case Flash chấm điểm rất rõ ràng (1 hoặc 5/5) — ở các điểm cực trị này 2 Judge hầu như luôn đồng thuận, nên việc luôn gọi thêm Pro không tạo thêm giá trị phân định mà chỉ tốn tiền. Escalation chỉ nên xảy ra ở vùng điểm mơ hồ (2–4), đúng nơi 2 model có khả năng bất đồng cao nhất — đây là lý do Cascade Judge giảm 54.1% cost mà avg_score không giảm (thậm chí tăng nhẹ, trong khoảng nhiễu thống kê).

## 3. Problem Solving

- Vấn đề: response của Judge model thỉnh thoảng không trả JSON thuần (kèm text dẫn nhập). Giải quyết tương tự nhóm SDG — dùng regex trích `{...}` trước khi parse, có fallback gán điểm 3 (trung bình) nếu parse lỗi để không làm crash toàn batch.
- Vấn đề rate limit 429 khi tăng `batch_size` lên 15 để chạy nhanh hơn: ban đầu pipeline crash giữa chừng. Giải quyết bằng retry + backoff trong `vertex_client.py`, đồng thời giảm `batch_size` về 8 trong `main.py` để cân bằng giữa tốc độ và độ ổn định — runtime giảm từ 397s xuống còn 321s cho 120 lần gọi agent (V1+V2, 60 case mỗi bản).
