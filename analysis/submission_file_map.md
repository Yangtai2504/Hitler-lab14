# Bản Đồ File Nộp Bài

| File/Thư mục | Tác dụng | Loại |
|---|---|---|
| `README.md` | Mô tả yêu cầu lab, lịch trình và cách chạy | Nhóm |
| `GRADING_RUBRIC.md` | Rubric chấm điểm nhóm/cá nhân | Nhóm |
| `requirements.txt` | Danh sách dependencies | Nhóm |
| `.gitignore` | Chặn `.env`, cache Python và golden dataset generated | Nhóm |
| `.env.example` | Mẫu biến môi trường cho Gemini judge, không chứa secret thật | Nhóm |
| `data/corpus.json` | Knowledge base nhỏ dùng cho RAG benchmark | Nhóm |
| `data/synthetic_gen.py` | Tạo `data/golden_set.jsonl` với 50+ test cases | Nhóm |
| `data/golden_set.jsonl` | Golden dataset generated khi chạy script, không commit theo README | Nhóm/generated |
| `data/HARD_CASES_GUIDE.md` | Gợi ý thiết kế hard cases/red teaming | Nhóm |
| `agent/main_agent.py` | RAG agent base/optimized để benchmark | Nhóm |
| `engine/retrieval_eval.py` | Tính Hit Rate, MRR, faithfulness, relevancy | Nhóm |
| `engine/llm_judge.py` | Multi-judge consensus, agreement rate, optional Gemini live mode | Nhóm |
| `engine/runner.py` | Async benchmark runner có concurrency guard | Nhóm |
| `engine/release_gate.py` | So sánh V1/V2 và quyết định Release/Rollback | Nhóm |
| `main.py` | Chạy benchmark, tạo reports và failure analysis | Nhóm |
| `check_lab.py` | Kiểm tra định dạng nộp bài | Nhóm |
| `reports/summary.json` | Tổng hợp metrics, regression và release gate sau khi chạy `main.py` | Nhóm/generated |
| `reports/benchmark_results.json` | Kết quả chi tiết từng case của candidate agent | Nhóm/generated |
| `reports/regression_comparison.json` | So sánh chi tiết baseline/candidate | Nhóm/generated |
| `analysis/failure_analysis.md` | Báo cáo nhóm: clustering lỗi, 5 Whys, action plan | Nhóm |
| `analysis/submission_file_map.md` | Bảng liệt kê file, tác dụng và phân loại nhóm/cá nhân | Nhóm |
| `analysis/reflections/reflection_Ten_SV.md` | Mẫu reflection cá nhân, mỗi thành viên copy/đổi tên theo mình | Cá nhân |
