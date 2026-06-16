# Individual Reflection — Nguyễn Thái Dương (2A202600823)

**Phụ trách:** Retrieval & SDG (Data team)
**Module chính:** `data/knowledge_base.py`, `engine/vector_store.py`, `engine/retrieval_eval.py`, `data/synthetic_gen.py`

## 1. Engineering Contribution

- Xây dựng knowledge base gồm 8 document chính sách hỗ trợ (đổi mật khẩu, hoàn tiền, vận chuyển, bảo mật tài khoản, subscription, hỗ trợ kỹ thuật, xóa tài khoản, API rate limit) trong `data/knowledge_base.py`, mỗi document có `id` riêng (`doc_001`–`doc_008`) để làm Ground Truth cho retrieval.
- Triển khai `VectorStore` (`engine/vector_store.py`) dùng `TfidfVectorizer` + `cosine_similarity` của scikit-learn làm retriever, trả về danh sách `doc_id` đã xếp hạng theo độ liên quan cho mỗi câu hỏi.
- Hoàn thiện `RetrievalEvaluator.evaluate_batch()` trong `engine/retrieval_eval.py`: tính Hit Rate và MRR thật trên toàn bộ dataset, có xử lý riêng các case không có ground-truth retrieval (`expected_retrieval_ids=[]`, ví dụ case red-team) bằng cờ `applicable=False` để không làm sai lệch điểm trung bình.
- Viết `data/synthetic_gen.py`: gọi Gemini 2.5 Flash qua Vertex AI để sinh dữ liệu — 6 cặp QA/document (48 case fact-check) cộng với 4 loại hard case x 3 lần (12 case: prompt injection, goal hijacking, out-of-context, ambiguous) → tổng 60 case, vượt yêu cầu tối thiểu 50.
- Kết quả đo được trên golden set: **Hit Rate = 0.77, MRR = 0.69** (ghi trong `reports/summary.json`).

## 2. Technical Depth

- **MRR (Mean Reciprocal Rank):** đo vị trí xuất hiện đầu tiên của tài liệu đúng trong danh sách kết quả retrieve, tính bằng `1/rank` (rank đếm từ 1). MRR cao hơn Hit Rate về độ chi tiết vì nó phạt nặng khi tài liệu đúng bị xếp hạng thấp, dù vẫn nằm trong top-k. Ví dụ: Hit Rate@4 = 1.0 nếu tài liệu đúng ở vị trí 1 hoặc vị trí 4 đều như nhau, nhưng MRR sẽ là 1.0 vs 0.25 — phân biệt rõ chất lượng ranking.
- **Trade-off Retrieval Quality vs Answer Quality:** trong benchmark thực tế, 5/7 case fail của agent là do retriever không đưa đúng tài liệu vào top-k (Hit Rate miss) → agent buộc phải trả lời "không có thông tin" dù KB có sẵn câu trả lời. Đây minh chứng rõ: nếu Retrieval sai, Generation không thể đúng bất kể model sinh câu trả lời tốt thế nào — củng cố lý do GRADING_RUBRIC.md yêu cầu bắt buộc đánh giá Retrieval riêng.
- **Hạn chế của TF-IDF:** retriever dùng sparse vector dựa trên overlap từ vựng, không nắm được ngữ nghĩa (semantic similarity). Câu hỏi paraphrase khác từ vựng với document gốc (vd "gói dịch vụ" vs liệt kê "Basic/Pro/Enterprise") dễ bị xếp hạng thấp dù nội dung liên quan — đây là root cause chính được ghi trong `analysis/failure_analysis.md`.

## 3. Problem Solving

- Vấn đề gặp phải: model sinh dữ liệu (Gemini) không luôn trả về JSON thuần, đôi khi kèm text giải thích hoặc markdown code block. Giải quyết bằng regex `re.search(r"\[.*\]", ...)` để trích JSON array trước khi `json.loads`, kèm fallback bỏ qua case lỗi parse thay vì crash toàn bộ pipeline sinh dữ liệu.
- Vấn đề về cân bằng dataset: nếu chỉ sinh case từ mỗi document riêng lẻ, dataset sẽ thiếu các case "khó" theo `data/HARD_CASES_GUIDE.md`. Giải quyết bằng cách tách riêng `HARD_CASE_SPECS` (4 loại red-team) và gọi sinh độc lập, đảm bảo đủ cả 2 nhóm: case thông thường (test accuracy) và case khó (test an toàn/robustness).
