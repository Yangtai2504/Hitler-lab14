# Individual Reflection — Nguyễn Ngọc Dũng (2A202600906)

**Phụ trách:** Failure Analysis, QA & Submission Validation
**Module chính:** `analysis/failure_analysis.md`, `check_lab.py`, bảo mật `.env` / `vertex-key.json`

## 1. Engineering Contribution

- Phân tích kết quả benchmark thật từ `reports/benchmark_results.json` (bản V2): trích các case có `status == "fail"` (judge final_score < 3), sắp xếp theo điểm thấp nhất, đối chiếu `retrieved_ids` thực tế với `expected_retrieval_ids` để xác định nguyên nhân là lỗi Retrieval hay lỗi Generation/Prompt.
- Viết `analysis/failure_analysis.md` với 3 phần dựa trên số liệu thật:
  - Failure Clustering: 5/7 case fail do "False Tôi không biết" (Retrieval miss), 1 case Partial Answer, 1 case Judge Calibration trên câu trả lời an toàn.
  - 5 Whys cho 3 case tệ nhất (đều có trích dẫn câu hỏi, điểm số, `retrieved_ids` thật từ report), kết luận root cause: retriever TF-IDF không bắt được semantic similarity, và chunking strategy "1 doc = 1 policy" quá thô.
  - Action Plan: đề xuất chuyển sang dense embedding, chunk nhỏ hơn, tách prompt riêng cho security/injection case, thêm rubric Judge cho "safety behavior".
- Phát hiện và xử lý rủi ro bảo mật: file `vertex-key.json` (service account credential) chưa nằm trong `.gitignore` ban đầu — đã bổ sung `vertex-key.json` và `venv/` vào `.gitignore` trước khi bất kỳ commit nào được tạo, xác nhận bằng `git status` rằng cả `.env` và `vertex-key.json` không xuất hiện trong danh sách file untracked sẽ bị thêm vào repo.
- Chạy `python check_lab.py` để xác minh định dạng nộp bài: xác nhận đủ 3 file bắt buộc (`reports/summary.json`, `reports/benchmark_results.json`, `analysis/failure_analysis.md`), đủ trường `metrics`/`metadata`, có Retrieval Metrics (hit_rate) và Multi-Judge Metrics (agreement_rate) — tránh bị trừ 5 điểm thủ tục do lỗi định dạng.
- Phát hiện lỗi nghiêm trọng khác trong `.gitignore` gốc của repo: dòng `reports/` khiến **toàn bộ thư mục `reports/`** (gồm 2 file bắt buộc nộp `summary.json`, `benchmark_results.json`) bị loại khỏi git, nghĩa là dù tồn tại trên máy, 2 file này sẽ **không lên được GitHub** khi push — vi phạm trực tiếp yêu cầu "Submission Checklist" trong README.md. Đã xóa dòng `reports/` khỏi `.gitignore` và xác nhận lại bằng `git status` rằng thư mục `reports/` giờ được track đúng.
- Rà soát lại đối chiếu README.md + GRADING_RUBRIC.md với toàn bộ repo sau khi code xong, phát hiện thêm 1 thiếu sót: chưa có đề xuất cụ thể "giảm 30% chi phí eval" như README yêu cầu (mục Tối ưu hiệu năng & Chi phí, 15%) — dù đã có cost report. Đã phối hợp với nhóm Multi-Judge để bổ sung thực nghiệm Cascade Judge và tài liệu `analysis/cost_optimization.md`.
- Phát hiện 5 Whys ban đầu (`analysis/failure_analysis.md`) thiếu bằng chứng cho yêu cầu "Có các bộ Red Teaming phá vỡ hệ thống thành công" (Dataset & SDG, 10đ) — soát lại `reports/benchmark_results.json` (mảng `v1`) và tìm ra 2 case `ambiguous` mà Agent V1 (Base) thực sự bị "phá": tự đoán bừa câu trả lời thay vì hỏi lại, bị Judge cho 1.0–2.0/5. Đã bổ sung dẫn chứng cụ thể này vào báo cáo nhóm.

## 2. Technical Depth

- **Vì sao phải tách "applicable" khi tính Hit Rate/MRR:** các case red-team (prompt injection, out-of-context, ambiguous) không có tài liệu "đúng" để so sánh (`expected_retrieval_ids = []`), nên nếu tính chung vào mẫu số trung bình sẽ làm sai lệch chỉ số Retrieval — một hệ thống Retrieval Eval đúng đắn phải phân biệt rõ "không áp dụng" với "áp dụng nhưng sai".
- **Phân biệt lỗi tầng Retrieval và tầng Generation khi đọc failure log:** quy trình QA dùng để debug là so `retrieved_ids` thực tế với `expected_retrieval_ids` trước khi đọc câu trả lời — nếu tài liệu đúng không nằm trong `retrieved_ids`, lỗi chắc chắn nằm ở Retrieval (Agent không có cách nào trả lời đúng dù prompt tốt thế nào); chỉ khi tài liệu đúng đã được retrieve mà câu trả lời vẫn sai, lúc đó mới kết luận lỗi ở Generation/Prompt. Đây chính là cách tách nguyên nhân gốc rễ theo yêu cầu "Root Cause" của GRADING_RUBRIC.md.
- **Hạn chế của Judge Calibration trên red-team case:** case prompt injection trong benchmark cho thấy cả 2 Judge đều cho điểm thấp (2/5) dù Agent đã từ chối đúng cách về mặt an toàn — vì Judge chấm theo độ khớp ngữ nghĩa với Ground Truth cụ thể, không có rubric riêng cho "hành vi an toàn nhưng diễn đạt khác". Đây là một giới hạn thật của hệ thống hiện tại, không phải lỗi ngẫu nhiên — cần ghi nhận để tránh đánh giá sai năng lực thật của Agent.

- **Vì sao việc "rà soát đối chiếu rubric" cần làm sau khi code xong, không chỉ làm 1 lần đầu:** rubric có nhiều tiêu chí nhỏ nằm rải rác (ví dụ yêu cầu "đề xuất giảm 30% chi phí" nằm trong đoạn mô tả văn xuôi, không nằm trong bảng checklist chính của README) — dễ bị bỏ sót nếu chỉ check theo checklist tổng. Quy trình QA đúng là đọc lại toàn văn rubric + README sau mỗi vòng implement, không chỉ dựa vào danh sách file cần nộp.

## 3. Problem Solving

- Vấn đề: một số module (`pypdf`, `ragas`, `pandas` trong `requirements.txt`) hiện chưa được dùng trực tiếp trong code (do pipeline dùng Vertex AI + TF-IDF thay vì RAGAS framework gốc) — quyết định giữ nguyên các dependency gốc trong `requirements.txt` (không xóa) để không phá vỡ giả định ban đầu của đề bài, đồng thời bổ sung thêm `google-genai` và `scikit-learn` là 2 thư viện thực sự được dùng.
- Vấn đề: phát hiện `vertex-key.json` (chứa private key thật của service account) bị mở trong IDE và nằm ngay tại root repo — đây là rủi ro lộ credential nếu commit nhầm. Đã xử lý ngay bằng cách thêm vào `.gitignore` trước khi tiếp tục bất kỳ thao tác git nào khác, và khuyến nghị nhóm tuyệt đối không chạy `git add -A` hoặc `git add .` mà chỉ add từng file cụ thể khi commit.
