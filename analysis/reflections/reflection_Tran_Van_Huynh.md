# Individual Reflection — Trần Văn Huỳnh (2A202600805)

**Phụ trách:** Agent Engineering (RAG + Prompt Optimization)
**Module chính:** `agent/main_agent.py`

## 1. Engineering Contribution

- Viết lại `agent/main_agent.py::MainAgent` (V1 — Base): RAG pipeline thật gồm 2 bước — retrieve top-3 document từ `VectorStore`, ghép context vào `BASE_SYSTEM_PROMPT` (prompt tối thiểu, chỉ yêu cầu "trả lời dựa trên context"), gọi `gemini-2.5-flash` qua `engine/vertex_client.generate()`.
- Viết `MainAgentV2` (Optimized) kế thừa từ `MainAgent`, thay đổi 2 điểm:
  - Tăng `top_k` từ 3 lên 4 để giảm rủi ro bỏ sót tài liệu đúng (đánh đổi: context dài hơn, tốn token hơn).
  - Đổi prompt thành `OPTIMIZED_SYSTEM_PROMPT` với 5 quy tắc rõ ràng: chỉ trả lời theo context, từ chối đúng cách khi thiếu thông tin, hỏi lại khi câu hỏi mơ hồ, từ chối khi bị yêu cầu làm việc ngoài phạm vi (goal hijacking), giữ tone chuyên nghiệp.
- Mỗi response trả về kèm `retrieved_ids` (phục vụ tính Hit Rate/MRR) và `metadata` (model, input/output tokens, cost) — dữ liệu này được `engine/runner.py` dùng trực tiếp để tổng hợp report mà không cần tính lại.
- Kết quả đo thật: V2 cải thiện avg_score từ 3.98 → 4.36 so với V1 trên cùng 60 case và cùng bộ Judge, chứng minh prompt engineering có tác động đo lường được.

## 2. Technical Depth

- **Vì sao tăng top_k không cải thiện Hit Rate:** dù V2 dùng top_k=4 (thêm 1 document so với V1's top_k=3), Hit Rate đo được của cả 2 bản đều là 0.77 — vì 2 bản dùng chung retriever TF-IDF, vấn đề Hit Rate miss nằm ở chất lượng ranking (document đúng bị xếp ngoài top-4, không chỉ ngoài top-3), không phải do số lượng document lấy ra. Đây là minh chứng rõ ràng cho việc tách biệt vấn đề ở tầng Retrieval và tầng Generation/Prompt khi debug agent.
- **Trade-off giữa "an toàn" (refuse khi không chắc) và "hữu ích" (trả lời đầy đủ):** prompt V2 buộc agent phải nói "tôi không có thông tin" khi context không đủ — điều này giảm hallucination nhưng cũng khiến agent từ chối cả những câu mà thực ra KB có câu trả lời (chỉ là retriever không lấy đúng tài liệu). Trong benchmark, 5/7 case fail của V2 là dạng từ chối "oan" như vậy — cho thấy chất lượng prompt chỉ phát huy hết tác dụng khi retrieval đủ tốt, hai tầng phải tối ưu cùng nhau.
- **Cost vs Quality của top_k cao hơn:** mỗi document thêm vào context làm tăng input token (tăng cost tuyến tính theo `PRICING_PER_1K_TOKENS`), nhưng cost trung bình/case đo được giữa V1 (~0.00104 USD) và V2 (~0.00110 USD) chỉ chênh khoảng 6% — chấp nhận được so với mức tăng +0.38 điểm chất lượng.

## 3. Problem Solving

- Vấn đề: prompt ban đầu (V1) không phân biệt rõ giữa "ngoài phạm vi" và "thiếu context", khiến model đôi khi trả lời lan man khi gặp câu hỏi goal-hijacking (ví dụ yêu cầu viết thơ). Giải quyết bằng cách thêm quy tắc số 4 trong `OPTIMIZED_SYSTEM_PROMPT` yêu cầu từ chối lịch sự và nhắc lại vai trò hỗ trợ khách hàng.
- Vấn đề: khi test agent độc lập qua `python agent/main_agent.py`, gặp lỗi `ModuleNotFoundError: No module named 'engine'` do chạy trực tiếp file thay vì chạy như module — đã thống nhất với nhóm là toàn bộ pipeline phải chạy với working directory ở gốc repo (`python -m agent.main_agent` hoặc qua `main.py`), tránh import path bị lệch.
