# Individual Reflection — Trần Đức Lương (2A202600881)

**Phụ trách:** Regression Release Gate (DevOps/Analyst team)
**Module chính:** `main.py`, `engine/runner.py`

## 1. Engineering Contribution

- Viết lại `engine/runner.py::BenchmarkRunner.run_single_test()` để nối toàn bộ pipeline thật cho mỗi case: gọi Agent → đo latency → tính Retrieval metrics qua `RetrievalEvaluator.evaluate_case()` → gọi `LLMJudge.evaluate_multi_judge()` → tổng hợp cost (agent + judge) và gắn `case_type` (fact-check/prompt_injection/goal_hijacking/...) để phục vụ failure clustering sau này.
- `run_all()` giữ cơ chế chạy song song theo batch bằng `asyncio.gather` (đã có sẵn từ template, được tinh chỉnh `batch_size` cùng nhóm Multi-Judge để tránh rate limit).
- Viết `main.py::build_summary()` tổng hợp các chỉ số thật: avg_score, pass_rate, hit_rate, mrr, agreement_rate, conflict_resolved_count, avg_latency_sec, total_cost_usd, avg_cost_per_case_usd.
- Triển khai `release_gate()`: logic Auto-Gate quyết định `APPROVE_RELEASE` hay `BLOCK_ROLLBACK` dựa trên 3 điều kiện đo được thật giữa Agent V2 (Optimized) so với V1 (Base):
  - `quality_ok`: delta avg_score của V2 so với V1 phải ≥ 0
  - `retrieval_ok`: Hit Rate của V2 không được giảm quá 5% so với V1 (`hit_rate_ratio >= 0.95`)
  - `latency_ok`: avg_latency_sec của V2 ≤ 15s
- Chạy thật benchmark V1 vs V2 trên 60 case: **V1 score 3.98 → V2 score 4.36 (delta +0.38)**, Hit Rate giữ nguyên 0.77 (vì 2 bản dùng chung retriever, chỉ khác prompt + top_k), quyết định cuối: **APPROVE_RELEASE**. Lưu kết quả vào `reports/summary.json` (mục `regression`) và `reports/benchmark_results.json`.

## 2. Technical Depth

- **Delta Analysis:** so sánh tuyệt đối giữa 2 phiên bản trên cùng một dataset/cùng một bộ Judge để đảm bảo so sánh công bằng (apple-to-apple) — nếu đổi judge hoặc đổi dataset giữa 2 lần chạy, delta sẽ không còn ý nghĩa vì nhiễu từ nguồn đo khác nhau, không phải do agent thay đổi.
- **Vì sao cần ngưỡng riêng cho Retrieval trong Release Gate:** một agent có thể "tăng điểm Judge" chỉ vì viết câu trả lời mượt hơn (tone tốt hơn) dù chất lượng retrieval không đổi hoặc giảm — nếu chỉ gate theo avg_score sẽ bỏ sót regression ở tầng retrieval. Đây là lý do thêm `retrieval_ok` làm điều kiện độc lập, đúng với tinh thần GRADING_RUBRIC.md (không đánh giá Generation mà bỏ qua Retrieval).
- **Trade-off Cost/Quality/Performance trong Gate:** Gate hiện tại ưu tiên Quality và Retrieval là điều kiện cứng (bắt buộc), còn latency chỉ là ngưỡng an toàn (15s/case — rất lỏng so với thực tế đo được ~1.9–2.5s/case) vì trong phạm vi lab, cost chưa được đưa vào Gate như một điều kiện chặn cứng — đây là hạn chế thật, có thể mở rộng thêm điều kiện `cost_ok` nếu muốn release gate chặt hơn về chi phí.

## 3. Problem Solving

- Vấn đề: pipeline tổng (V1 + V2, 120 lượt gọi agent x kèm 2-3 lượt gọi judge mỗi case) ban đầu chạy 397s — vượt khá xa mốc "<2 phút/50 case" trong rubric (vốn áp dụng cho 1 lần benchmark, không phải 2 phiên bản gộp lại). Đã thử tăng `batch_size` lên 15 để chạy nhanh hơn nhưng gây lỗi 429 (rate limit Vertex Express Mode); phối hợp với nhóm Multi-Judge để thêm retry/backoff và chốt `batch_size=8` làm điểm cân bằng, giảm runtime xuống 321s.
- Vấn đề: cần phân biệt rõ giữa "không có Retrieval Ground Truth" (case red-team/out-of-context) và "Retrieval sai" khi tính trung bình Hit Rate/MRR ở tầng tổng hợp summary — nếu tính cả case không áp dụng (`expected_retrieval_ids=[]`) vào mẫu số sẽ làm sai lệch số liệu. Giải quyết bằng cách lọc theo cờ `applicable` trước khi tính trung bình trong `build_summary()`.
