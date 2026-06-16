# Tối ưu Chi phí Eval — Cascade Multi-Judge

## Vấn đề
Trong benchmark thật trên 60 case (`reports/benchmark_results.json`, agent V2), chi phí Judge
chiếm **75.6%** tổng chi phí eval (`0.0495 USD` / `0.0655 USD` tổng), vì kiến trúc Multi-Judge
mặc định (`engine/llm_judge.py::evaluate_multi_judge`) luôn gọi **cả 2 model** (Gemini 2.5 Flash
+ Gemini 2.5 Pro) cho **mọi** case, dù Pro đắt hơn Flash khoảng 4x (input) / 2x (output) theo
bảng giá trong `engine/vertex_client.py::PRICING_PER_1K_TOKENS`.

Quan sát từ dữ liệu thật: trong 60 case, điểm của Flash phân bố `{5: 46, 4: 5, 3: 1, 2: 4, 1: 4}`
— tức **85% case Flash đã cho điểm rất rõ ràng (1 hoặc 5)**, và ở các case này 2 Judge hầu như
luôn đồng thuận. Việc luôn gọi thêm Pro cho cả những case "hiển nhiên" này là lãng phí.

## Đề xuất: Cascade Judge
Thêm phương thức `LLMJudge.evaluate_multi_judge_cascade()` (file `engine/llm_judge.py`):
1. Luôn gọi Flash (model rẻ) trước.
2. Nếu điểm Flash là **1 hoặc 5** (rõ ràng thất bại/thành công) → chấp nhận điểm này, **không
   gọi Pro**.
3. Nếu điểm Flash nằm trong vùng **2–4** (không chắc chắn) → escalate gọi thêm Pro, áp dụng lại
   đúng logic xử lý xung đột (tie-breaker khi lệch > 1) như chế độ Multi-Judge gốc.

Đây **vẫn là kiến trúc Multi-Judge với ≥ 2 model khác nhau** (không vi phạm yêu cầu rubric về
"ít nhất 2 Judge") — chỉ khác là model thứ 2 được gọi **có điều kiện** thay vì luôn luôn. Chế độ
gốc `evaluate_multi_judge()` (luôn gọi 2 model) vẫn được giữ làm mặc định trong `main.py` để đảm
bảo benchmark chính thức luôn dùng đủ 2 Judge cho mọi case.

## Kết quả đo thật
Thực nghiệm tại `analysis/cost_optimization_experiment.py`: chạy lại Cascade Judge trên **chính
60 cặp (câu hỏi, câu trả lời thật của agent V2, ground truth)** đã có trong
`reports/benchmark_results.json` — không gọi lại Agent, chỉ đo riêng phần chi phí Judge để so
sánh công bằng. Kết quả lưu tại `analysis/cost_optimization_result.json`:

| Chỉ số | Full Multi-Judge (gốc) | Cascade Judge | Thay đổi |
|---|---|---|---|
| Tổng chi phí Judge (60 case) | 0.049543 USD | 0.022720 USD | **−54.1%** |
| Điểm trung bình (avg_score) | 4.358 | 4.383 | +0.025 (không giảm độ chính xác) |
| Số case phải escalate sang Pro | 60/60 (100%) | 13/60 (21.7%) | |

→ **Giảm được 54.1% chi phí Eval**, vượt mục tiêu 30% đề ra trong README, đồng thời độ chính xác
(avg_score) không giảm mà còn nhích nhẹ lên — vì các case Pro được gọi đúng vào nhóm "không chắc
chắn" (nơi Pro thực sự đóng góp giá trị phân định), còn ở các case đã rõ ràng thì Flash một mình
đã đủ tin cậy.

## Khuyến nghị
- Dùng `evaluate_multi_judge_cascade()` cho các vòng eval lặp lại thường xuyên (CI/regression
  hàng ngày) để tiết kiệm chi phí.
- Giữ `evaluate_multi_judge()` (full 2-model) cho lần benchmark chính thức nộp bài và các đợt
  audit định kỳ, để đảm bảo Agreement Rate được đo trên toàn bộ dataset, không bị thiên lệch bởi
  cơ chế escalation.
